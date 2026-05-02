from io import BytesIO

import pytest
import torch
from PIL import Image

from services.image_service import ImageService


class DummyResponse:
    def __init__(self, content=b""):
        self.content = content

    def raise_for_status(self):
        return None


def build_test_image_bytes():
    image = Image.new("RGB", (32, 32), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_download_image_from_url_returns_rgb_image(monkeypatch):
    image_bytes = build_test_image_bytes()
    monkeypatch.setattr("services.image_service.requests.get", lambda url: DummyResponse(image_bytes))

    image = ImageService.download_image_from_url("https://example.com/test.png")

    assert image.mode == "RGB"
    assert image.size == (32, 32)


def test_analyse_returns_uncertain_when_confidence_is_below_threshold(monkeypatch):
    monkeypatch.setattr(ImageService, "download_image_from_url", classmethod(lambda cls, url: "image"))
    monkeypatch.setattr(ImageService, "preprocess_image_for_inference", classmethod(lambda cls, image: "tensor"))
    monkeypatch.setattr(ImageService, "run_model_inference", classmethod(lambda cls, tensor: (2, 4.2, 0.42)))

    response = ImageService.analyse("https://example.com/test.png")

    assert response.room_type == "uncertain"
    assert response.condition_score is None
    assert response.confidence == pytest.approx(0.42)


def test_analyse_returns_room_type_and_normalized_condition_score(monkeypatch):
    monkeypatch.setattr(ImageService, "download_image_from_url", classmethod(lambda cls, url: "image"))
    monkeypatch.setattr(ImageService, "preprocess_image_for_inference", classmethod(lambda cls, image: "tensor"))
    monkeypatch.setattr(ImageService, "run_model_inference", classmethod(lambda cls, tensor: (0, 5.8, 0.97)))

    response = ImageService.analyse("https://example.com/test.png")

    assert response.room_type == "kitchen"
    assert response.condition_score == 5
    assert response.confidence == pytest.approx(0.97)


def test_preprocess_image_for_inference_returns_normalized_tensor():
    image = Image.new("RGB", (64, 64), color="white")

    tensor = ImageService.preprocess_image_for_inference(image)

    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (3, 224, 224)


def test_resolve_room_type_returns_other_for_unknown_index():
    assert ImageService.resolve_room_type_from_prediction(99) == "other"


def test_normalize_condition_score_clamps_range():
    assert ImageService.normalize_condition_score(0.1) == 1
    assert ImageService.normalize_condition_score(3.4) == 3
    assert ImageService.normalize_condition_score(9.9) == 5
