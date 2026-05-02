"""Streamlit entrypoint for the aiPropertyTriageProject WebUI."""

from pathlib import Path
import sys

import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from config import Config
from controllers.chat_controller import ChatController
from controllers.listing_controller import ListingController
from services.chat_service import ChatService
from services.listing_service import ListingService
from services.prompt_service import PromptService


def configure_page() -> None:
    """Apply shared Streamlit page settings."""
    st.set_page_config(page_title=Config.APP_TITLE, layout="wide")


def initialize_session_state() -> None:
    """Initialize the shared Streamlit session keys used by the UI."""
    st.session_state.setdefault("chat_history", [])

    # Backward-compatible migration if a previous format was used.
    if st.session_state["chat_history"] and isinstance(st.session_state["chat_history"][0], tuple):
        migrated = []
        for role, content in st.session_state["chat_history"]:
            migrated.append({"role": role, "content": content})
        st.session_state["chat_history"] = migrated


def render_chat_sidebar() -> None:
    """Show prompt and connection metadata in the sidebar."""
    st.sidebar.header("Assistant Settings")
    st.sidebar.caption("Prompt selection is driven by environment config for now.")

    st.sidebar.text(f"Prompt file: {PromptService.get_prompt_path().name}")
    st.sidebar.text(f"Model: {Config.OLLAMA_MODEL}")
    st.sidebar.text(f"Ollama: {Config.OLLAMA_HOST}:{Config.OLLAMA_PORT}")

    if st.sidebar.button("Clear Chat", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()


def render_chat_tab() -> None:
    """Render the conversational assistant UI."""
    render_chat_sidebar()

    st.subheader("Conversational Assistant")
    st.caption(
        "Real-estate only. Off-topic questions will be refused. "
        f"Active prompt: `{PromptService.get_prompt_path().name}`."
    )

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_text = st.chat_input("Ask about listings, buying, selling, or renting…")
    if not user_text:
        return

    st.session_state["chat_history"].append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Contacting Ollama…"):
            try:
                chat_request = ChatController.build_request(user_text)
                chat_response = ChatService.chat(chat_request)
                assistant_text = chat_response.reply
            except Exception as exc:
                assistant_text = f"[Error contacting Ollama: {exc}]"
        st.markdown(assistant_text)

    st.session_state["chat_history"].append({"role": "assistant", "content": assistant_text})


def _parse_image_urls(raw_image_urls: str) -> list[str]:
    """Split comma-separated image URLs into a normalized list."""
    return [item.strip() for item in raw_image_urls.split(",") if item.strip()]


def _parse_uploaded_urls(file_content: bytes) -> list[str]:
    """Parse newline or comma-separated URLs from an uploaded text/csv file."""
    text = file_content.decode("utf-8", errors="ignore")
    normalized = text.replace("\r", "\n").replace(",", "\n")
    return [item.strip() for item in normalized.split("\n") if item.strip()]


def render_listing_response(summary: str, recommendations: list[str], image_scores: list[dict]) -> None:
    """Render structured listing response elements in the UI."""
    st.success("Listing submitted successfully.")
    st.markdown(f"**Summary:** {summary}")

    st.markdown("**Recommendations**")
    if recommendations:
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.caption("No recommendations returned.")

    st.markdown("**Image Scores**")
    if image_scores:
        st.dataframe(image_scores, use_container_width=True)
    else:
        st.caption("No image scores returned.")


def render_listing_tab() -> None:
    """Render the listing submission workflow UI."""
    st.subheader("Listing Submission")
    st.caption("Submit listing metadata to the configured n8n triage webhook.")

    with st.form("listing_submission_form"):
        agent_name = st.text_input("Agent Name")
        listing_description = st.text_area("Listing Description", height=180)
        image_urls_raw = st.text_area(
            "Image URLs (comma-separated)",
            help="Paste one or more URLs separated by commas.",
        )
        image_urls_file = st.file_uploader(
            "Or upload a TXT/CSV file containing image URLs",
            type=["txt", "csv"],
        )
        submitted = st.form_submit_button("Submit to n8n", use_container_width=True)

    if not submitted:
        return

    try:
        urls_from_text = _parse_image_urls(image_urls_raw)
        urls_from_file = _parse_uploaded_urls(image_urls_file.getvalue()) if image_urls_file else []
        combined_urls = list(dict.fromkeys(urls_from_text + urls_from_file))

        request = ListingController.build_request(
            agent_name=agent_name,
            listing_description=listing_description,
            image_urls=combined_urls,
        )
        result = ListingService.submit(request)
    except Exception as exc:
        st.error(f"Listing submission failed: {exc}")
        return

    image_rows = [item.model_dump() for item in result.image_scores]
    render_listing_response(
        summary=result.summary,
        recommendations=result.recommendations,
        image_scores=image_rows,
    )


def render_app_shell() -> None:
    """Render the main WebUI shell with assistant and listing tabs."""
    st.title(Config.APP_TITLE)
    st.caption("Phase 3: conversational assistant and n8n listing submission are wired.")

    assistant_tab, listing_tab = st.tabs(Config.WEBUI_TABS)

    with assistant_tab:
        render_chat_tab()

    with listing_tab:
        render_listing_tab()


def main() -> None:
    """Run the Streamlit application."""
    configure_page()
    initialize_session_state()
    render_app_shell()


if __name__ == "__main__":
    main()
