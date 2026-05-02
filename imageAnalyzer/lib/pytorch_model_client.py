
"""
PyTorch EfficientNet-B0 model client for room type classification and condition score regression.
"""

import os

import torch
import torch.nn as nn

try:
    import timm
except ImportError:  # pragma: no cover - exercised indirectly in runtime environments
    timm = None

class EfficientNetMultiHead(nn.Module):
    def __init__(self, num_classes=5):
        super().__init__()
        self.backbone = self.create_frozen_backbone()
        in_features = self.backbone.num_features
        self.classifier = nn.Linear(in_features, num_classes)
        self.regressor = nn.Linear(in_features, 1)

    @staticmethod
    def create_frozen_backbone():
        if timm is None:
            raise ImportError("timm is required to initialize EfficientNetMultiHead.")

        backbone = timm.create_model("efficientnet_b0", pretrained=True, num_classes=0)
        for param in backbone.parameters():
            param.requires_grad = False
        return backbone

    def forward(self, x):
        features = self.backbone(x)
        class_logits = self.classifier(features)
        condition_score = self.regressor(features)
        return class_logits, condition_score

class PytorchModelClient:
    def __init__(self, model_path=None, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = EfficientNetMultiHead()
        if model_path:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model checkpoint not found: {model_path}")

            try:
                state_dict = torch.load(model_path, map_location=self.device, weights_only=True)
            except TypeError:
                state_dict = torch.load(model_path, map_location=self.device)

            try:
                self.model.load_state_dict(state_dict)
            except RuntimeError as exc:
                raise RuntimeError(
                    f"Failed to load checkpoint '{model_path}'. Ensure checkpoint architecture matches runtime model."
                ) from exc
        self.model.to(self.device)
        self.model.eval()

    @torch.no_grad()
    def predict(self, image_tensor):
        image_tensor = image_tensor.unsqueeze(0).to(self.device)
        class_logits, condition_score = self.model(image_tensor)
        class_probs = torch.softmax(class_logits, dim=1)
        pred_class = class_probs.argmax(dim=1).item()
        confidence = class_probs.max(dim=1).values.item()
        pred_score = condition_score.squeeze().item()
        return pred_class, pred_score, confidence
