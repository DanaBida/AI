"""Controller helpers for the listing submission surface."""

from models.listing_types import ListingSubmissionRequest


class ListingController:
    """Builds validated listing submission payloads."""

    @classmethod
    def build_request(
        cls,
        agent_name: str,
        listing_description: str,
        image_urls: list[str],
    ) -> ListingSubmissionRequest:
        """Create a validated listing submission request."""
        return ListingSubmissionRequest(
            agent_name=agent_name.strip(),
            listing_description=listing_description.strip(),
            image_urls=[url.strip() for url in image_urls if url.strip()],
        )
