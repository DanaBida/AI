import pytest
import torch

from lib import pytorch_model_client
from lib.pytorch_model_client import PytorchModelClient


class DummyModel:
    def __init__(self):
        self.loaded_state = None
        self.target_device = None
        self.eval_called = False

    def load_state_dict(self, state):
        self.loaded_state = state

    def to(self, device):
        self.target_device = device
        return self

    def eval(self):
        self.eval_called = True
        return self

    def __call__(self, image_tensor):
        class_logits = torch.tensor([[0.1, 0.9, 0.0, 0.0, 0.0, 0.0]], dtype=torch.float32)
        condition_score = torch.tensor([[3.6]], dtype=torch.float32)
        return class_logits, condition_score


def test_predict_returns_predicted_class_score_and_confidence(monkeypatch):
    dummy_model = DummyModel()
    monkeypatch.setattr(pytorch_model_client, "EfficientNetMultiHead", lambda: dummy_model)

    client = PytorchModelClient(model_path=None, device="cpu")
    pred_class, pred_score, confidence = client.predict(torch.zeros((3, 224, 224)))

    assert pred_class == 1
    assert pred_score == pytest.approx(3.6)
    assert confidence == pytest.approx(0.3194867, rel=1e-5)
    assert dummy_model.target_device == "cpu"
    assert dummy_model.eval_called is True


def test_model_weights_are_loaded_when_path_is_provided(monkeypatch):
    dummy_model = DummyModel()
    monkeypatch.setattr(pytorch_model_client, "EfficientNetMultiHead", lambda: dummy_model)
    monkeypatch.setattr(pytorch_model_client.torch, "load", lambda path, map_location: {"path": path, "device": map_location})

    PytorchModelClient(model_path="weights.pt", device="cpu")

    assert dummy_model.loaded_state == {"path": "weights.pt", "device": "cpu"}
