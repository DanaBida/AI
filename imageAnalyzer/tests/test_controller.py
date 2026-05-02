from fastapi.testclient import TestClient

from app import app
from services.image_service import ImageService


client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyse_endpoint_returns_service_response(monkeypatch):
    monkeypatch.setattr(
        ImageService,
        "analyse",
        classmethod(
            lambda cls, image_url: {
                "room_type": "bathroom",
                "condition_score": 4,
                "confidence": 0.91,
            }
        ),
    )

    response = client.post("/analyse", json={"image_url": "https://example.com/image.jpg"})

    assert response.status_code == 200
    assert response.json() == {
        "room_type": "bathroom",
        "condition_score": 4,
        "confidence": 0.91,
    }


def test_analyse_endpoint_returns_500_when_service_fails(monkeypatch):
    def raise_error(cls, image_url):
        raise RuntimeError("inference failed")

    monkeypatch.setattr(ImageService, "analyse", classmethod(raise_error))

    response = client.post("/analyse", json={"image_url": "https://example.com/image.jpg"})

    assert response.status_code == 500
    assert response.json() == {"detail": "inference failed"}
