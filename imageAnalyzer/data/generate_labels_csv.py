"""Generate labels.csv for training from dataset split CSV files."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

STYLE_TO_SCORE = {
    "modern": 4.5,
    "scandinavian": 4.0,
    "minimalist": 3.5,
    "industrial": 3.0,
    "boho": 3.2,
}


def normalize_room_type(room_type: str) -> str:
    if room_type == "living_room":
        return "living room"
    return room_type


def normalize_image_path(original_path: str) -> str:
    marker = "../data/raw/"
    if original_path.startswith(marker):
        return original_path[len(marker) :]
    return original_path


def load_rows(split_csv: Path, split: str) -> list[dict[str, str | float]]:
    rows: list[dict[str, str | float]] = []
    with split_csv.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            style = row["style"].strip().lower()
            rows.append(
                {
                    "image_path": normalize_image_path(row["image_path"].strip()),
                    "room_type": normalize_room_type(row["room_type"].strip().lower()),
                    "condition_score": STYLE_TO_SCORE.get(style, 3.5),
                    "split": split,
                }
            )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate labels.csv for imageAnalyzer training.")
    parser.add_argument(
        "--dataset-root",
        default="./data/raw/Pinterest Interior Design Images and Metadata",
        help="Root folder that contains train_data.csv / val_data.csv / test_data.csv",
    )
    parser.add_argument(
        "--output",
        default="./data/raw/labels.csv",
        help="Output labels CSV path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_root = Path(args.dataset_root)
    output_path = Path(args.output)

    train_csv = dataset_root / "train_data.csv"
    val_csv = dataset_root / "val_data.csv"
    test_csv = dataset_root / "test_data.csv"

    rows = []
    rows.extend(load_rows(train_csv, "train"))
    rows.extend(load_rows(val_csv, "val"))
    rows.extend(load_rows(test_csv, "test"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image_path", "room_type", "condition_score", "split"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} label rows at {output_path}")


if __name__ == "__main__":
    main()
