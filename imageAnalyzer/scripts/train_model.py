
"""Train EfficientNet multi-head model with transfer learning for room type and condition score."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import Config
from lib.pytorch_model_client import EfficientNetMultiHead

ROOM_TYPES = ["kitchen", "bathroom", "living room", "bedroom", "other"]


class RoomConditionDataset(Dataset):
    """CSV-driven image dataset for room classification and condition score regression."""

    def __init__(self, labels_csv: Path, images_root: Path, split: str, transform):
        self.transform = transform
        self.samples: list[tuple[Path, int, float]] = []

        with labels_csv.open("r", encoding="utf-8") as file_handle:
            reader = csv.DictReader(file_handle)
            for row in reader:
                if row["split"].strip().lower() != split:
                    continue

                room_type = row["room_type"].strip().lower()
                if room_type not in ROOM_TYPES:
                    raise ValueError(f"Unknown room_type '{room_type}' in {labels_csv}")

                score = float(row["condition_score"])
                if score < 1 or score > 5:
                    raise ValueError(f"condition_score must be within [1,5], got {score}")

                image_path = images_root / row["image_path"].strip()
                if not image_path.exists():
                    raise FileNotFoundError(f"Missing image referenced in CSV: {image_path}")

                self.samples.append((image_path, ROOM_TYPES.index(room_type), score))

        if not self.samples:
            raise ValueError(f"No samples found for split='{split}' in {labels_csv}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        image_path, room_index, condition_score = self.samples[index]
        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image)
        room_label = torch.tensor(room_index, dtype=torch.long)
        score_label = torch.tensor(condition_score, dtype=torch.float32)
        return tensor, room_label, score_label


def build_transforms():
    train_transform = transforms.Compose(
        [
            transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=12),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )

    eval_transform = transforms.Compose(
        [
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    return train_transform, eval_transform


def create_dataloaders(labels_csv: Path, images_root: Path, batch_size: int):
    train_transform, eval_transform = build_transforms()
    train_ds = RoomConditionDataset(labels_csv=labels_csv, images_root=images_root, split="train", transform=train_transform)
    val_ds = RoomConditionDataset(labels_csv=labels_csv, images_root=images_root, split="val", transform=eval_transform)
    test_ds = RoomConditionDataset(labels_csv=labels_csv, images_root=images_root, split="test", transform=eval_transform)

    total_images = len(train_ds) + len(val_ds) + len(test_ds)
    if total_images < 200:
        raise ValueError(f"Dataset must include at least 200 labeled images, found {total_images}")

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader, test_loader, total_images


def train_one_epoch(model, dataloader, optimizer, criterion_cls, criterion_reg, device):
    model.train()
    running_loss = 0.0

    for images, labels, scores in dataloader:
        images = images.to(device)
        labels = labels.to(device)
        scores = scores.to(device)

        optimizer.zero_grad()
        class_logits, condition_pred = model(images)
        loss_cls = criterion_cls(class_logits, labels)
        loss_reg = criterion_reg(condition_pred.squeeze(1), scores)
        loss = loss_cls + loss_reg
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * images.size(0)

    return running_loss / len(dataloader.dataset)


@torch.no_grad()
def evaluate(model, dataloader, device):
    model.eval()
    correct = 0
    total = 0
    absolute_error = 0.0

    for images, labels, scores in dataloader:
        images = images.to(device)
        labels = labels.to(device)
        scores = scores.to(device)

        class_logits, condition_pred = model(images)
        predictions = class_logits.argmax(dim=1)
        correct += (predictions == labels).sum().item()
        total += labels.size(0)

        batch_mae = (condition_pred.squeeze(1) - scores).abs().sum().item()
        absolute_error += batch_mae

    accuracy = correct / total if total else 0.0
    mae = absolute_error / total if total else 0.0
    return accuracy, mae


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train EfficientNet multi-head room + condition model.")
    parser.add_argument("--labels-csv", default=str(Path(Config.RAW_DATA_DIR) / "labels.csv"))
    parser.add_argument("--images-root", default=Config.RAW_DATA_DIR)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--patience", type=int, default=6)
    parser.add_argument("--min-target-accuracy", type=float, default=0.80)
    return parser.parse_args()


def train_model(args: argparse.Namespace):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    labels_csv = Path(args.labels_csv)
    images_root = Path(args.images_root)

    train_loader, val_loader, test_loader, total_images = create_dataloaders(
        labels_csv=labels_csv,
        images_root=images_root,
        batch_size=args.batch_size,
    )

    model = EfficientNetMultiHead(num_classes=len(ROOM_TYPES)).to(device)
    criterion_cls = nn.CrossEntropyLoss()
    criterion_reg = nn.SmoothL1Loss()
    optimizer = optim.Adam((p for p in model.parameters() if p.requires_grad), lr=args.learning_rate)

    output_dir = Path(Config.MODEL_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "efficientnet_multihead_best.pt"
    metrics_path = output_dir / "training_metrics.json"

    best_val_acc = 0.0
    best_epoch = 0
    patience_counter = 0

    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(
            model=model,
            dataloader=train_loader,
            optimizer=optimizer,
            criterion_cls=criterion_cls,
            criterion_reg=criterion_reg,
            device=device,
        )
        val_acc, val_mae = evaluate(model=model, dataloader=val_loader, device=device)

        print(
            f"Epoch {epoch}/{args.epochs} | train_loss={train_loss:.4f} "
            f"| val_acc={val_acc:.4f} | val_mae={val_mae:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            patience_counter = 0
            torch.save(model.state_dict(), checkpoint_path)
        else:
            patience_counter += 1

        if best_val_acc >= args.min_target_accuracy:
            print(f"Stopping early: reached target val accuracy {best_val_acc:.4f}")
            break

        if patience_counter >= args.patience:
            print("Stopping early: validation accuracy plateaued.")
            break

    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    test_acc, test_mae = evaluate(model=model, dataloader=test_loader, device=device)

    metrics = {
        "dataset_total_images": total_images,
        "room_types": ROOM_TYPES,
        "base_model": "efficientnet_b0_pretrained",
        "transfer_learning": "frozen_backbone_train_heads",
        "augmentation": {
            "train": [
                "RandomResizedCrop(224, scale=(0.7, 1.0))",
                "RandomHorizontalFlip(0.5)",
                "RandomRotation(12)",
                "ColorJitter(0.2,0.2,0.2)",
                "ImageNet normalization",
            ],
            "eval": ["Resize(256)", "CenterCrop(224)", "ImageNet normalization"],
        },
        "best_val_accuracy": round(best_val_acc, 4),
        "best_epoch": best_epoch,
        "final_test_accuracy": round(test_acc, 4),
        "final_test_condition_mae": round(test_mae, 4),
        "checkpoint_path": str(checkpoint_path),
    }

    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Best validation accuracy: {best_val_acc:.4f} (epoch {best_epoch})")
    print(f"Final test accuracy: {test_acc:.4f}")
    print(f"Final test condition MAE: {test_mae:.4f}")
    print(f"Saved checkpoint: {checkpoint_path}")
    print(f"Saved metrics: {metrics_path}")


if __name__ == "__main__":
    train_model(parse_args())
