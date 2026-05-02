"""Service layer for listing submission interactions."""

from lib.n8n_client import N8NClient
from models.listing_types import ListingRecommendation, ListingSubmissionRequest


_SHARED_N8N_CLIENT = N8NClient()


class ListingService:
    """Business logic for sending listing submissions to n8n."""

    _client = _SHARED_N8N_CLIENT

    @classmethod
    def submit(cls, request: ListingSubmissionRequest) -> ListingRecommendation:
        """Submit a validated request to n8n and normalize the response."""
        result = cls._client.submit_listing(
            agent_name=request.agent_name,
            listing_description=request.listing_description,
            image_urls=request.image_urls,
        )

        return ListingRecommendation.model_validate(result)
