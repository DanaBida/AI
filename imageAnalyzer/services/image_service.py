
"""
ImageService: Handles image download, preprocessing, inference, and confidence logic.
"""

import requests
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from requests import RequestException
from torchvision import transforms
from config import Config
from lib.pytorch_model_client import PytorchModelClient
from models.image_types import ImageAnalysisResponse


class ImageServiceError(Exception):
    pass


class ImageDownloadError(ImageServiceError):
    pass


class ImagePreprocessError(ImageServiceError):
    pass


class ModelInferenceError(ImageServiceError):
    pass


class ImageService:
    ROOM_TYPES = ["kitchen", "bathroom", "living room", "bedroom", "other"]
    CONFIDENCE_THRESHOLD = Config.CONFIDENCE_THRESHOLD
    MODEL_PATH = Config.MODEL_PATH
    _model_client = None

    @classmethod
    def get_model_client(cls):
        if cls._model_client is None:
            cls._model_client = PytorchModelClient(model_path=cls.MODEL_PATH)
        return cls._model_client

    @classmethod
    def analyse(cls, image_url: str) -> ImageAnalysisResponse:
        image = cls.download_image_from_url(image_url)
        tensor = cls.preprocess_image_for_inference(image)
        pred_class_idx, pred_score, confidence = cls.run_model_inference(tensor)

        if confidence < cls.CONFIDENCE_THRESHOLD:
            return ImageAnalysisResponse(
                room_type="uncertain",
                condition_score=None,
                confidence=confidence,
            )

        room_type = cls.resolve_room_type_from_prediction(pred_class_idx)
        condition_score = cls.normalize_condition_score(pred_score)
        return ImageAnalysisResponse(
            room_type=room_type,
            condition_score=condition_score,
            confidence=confidence,
        )

    @classmethod
    def download_image_from_url(cls, image_url: str) -> Image.Image:
        try:
            response = requests.get(image_url, timeout=15)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGB")
        except RequestException as exc:
            raise ImageDownloadError(f"Failed to download image from URL: {image_url}") from exc
        except UnidentifiedImageError as exc:
            raise ImageDownloadError("Downloaded content is not a valid image format") from exc
        except OSError as exc:
            raise ImageDownloadError("Unable to decode image bytes") from exc

    @classmethod
    def preprocess_image_for_inference(cls, image: Image.Image):
        try:
            preprocess = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])
            return preprocess(image)
        except Exception as exc:
            raise ImagePreprocessError("Failed to preprocess image for inference") from exc

    @classmethod
    def run_model_inference(cls, tensor):
        try:
            return cls.get_model_client().predict(tensor)
        except Exception as exc:
            raise ModelInferenceError("Model inference failed") from exc

    @classmethod
    def resolve_room_type_from_prediction(cls, pred_class_idx: int) -> str:
        if pred_class_idx < len(cls.ROOM_TYPES):
            return cls.ROOM_TYPES[pred_class_idx]
        return "other"

    @classmethod
    def normalize_condition_score(cls, pred_score: float) -> int:
        return int(round(max(1, min(5, pred_score))))
