"""Final prompt templates and prompt-engineering metadata for the RAG service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List


SYSTEM_PROMPT = (
    "You are a careful real-estate analysis assistant.\n"
    "Use only the retrieved listings provided to you.\n"
    "Do not invent property facts, prices, locations, or amenities.\n"
    "If the context is insufficient, say so clearly.\n"
    "Support every conclusion with explicit property-id citations."
)

RETRIEVAL_PROMPT_TEMPLATE = (
    "{system_prompt}\n\n"
    "Retrieved listings:\n"
    "{context}\n\n"
    "User query:\n"
    "{query}\n\n"
    "Response requirements:\n"
    "1. Summarize the closest market matches.\n"
    "2. Explain the reasoning using only retrieved facts.\n"
    "3. Cite property ids inline, for example [prop_001].\n"
    "4. Mention uncertainty when context does not fully support a claim."
)

CITATION_INSTRUCTION = (
    "Every pricing, location, or feature claim must include at least one matching property-id citation in brackets."
)

HALLUCINATION_GUARD = (
    "Never add details that are absent from the retrieved listings. "
    "If a requested detail is missing, explicitly say it was not present in the retrieved context."
)

OUTPUT_FORMAT_INSTRUCTION = (
    "Return two short paragraphs titled 'Matches' and 'Insight'. Keep the answer concise and factual."
)

RELEVANCE_FILTER_INSTRUCTION = (
    "Prefer listings that match the user's requested location, room count, condition, and price range. "
    "Ignore retrieved facts that are clearly unrelated."
)


@dataclass(frozen=True)
class PromptSurfaceMetadata:
    """Metadata about the winning prompt iteration for a specific surface."""

    surface_name: str
    winning_iteration: str
    pass_rate: str
    recorded_on: str
    focus: str
    final_prompt: str
    design_decisions: List[str]
    lessons_learned: List[str]


PROMPT_SURFACE_METADATA: Dict[str, PromptSurfaceMetadata] = {
    "surface_1": PromptSurfaceMetadata(
        surface_name="Citation format",
        winning_iteration="v5-template",
        pass_rate="pending empirical run",
        recorded_on=str(date.today()),
        focus="Require inline property-id citations for every material claim.",
        final_prompt=(
            f"{SYSTEM_PROMPT}\n\n"
            f"{CITATION_INSTRUCTION}\n"
            f"{OUTPUT_FORMAT_INSTRUCTION}"
        ),
        design_decisions=[
            "The safety-oriented system prompt sets a non-negotiable rule that every conclusion must stay grounded in retrieved evidence.",
            "The citation instruction is explicit about inline property-id brackets so reviewers can validate claims quickly.",
            "The short labeled output format reduces drift into long unsupported prose and makes citation checking easier.",
        ],
        lessons_learned=[
            "Direct citation rules work better than vague requests to mention sources.",
            "Short output structures reduce the chance that citations disappear in long narrative text.",
        ],
    ),
    "surface_2": PromptSurfaceMetadata(
        surface_name="Hallucination prevention",
        winning_iteration="v5-template",
        pass_rate="pending empirical run",
        recorded_on=str(date.today()),
        focus="Force explicit uncertainty when context is incomplete.",
        final_prompt=(
            f"{SYSTEM_PROMPT}\n\n"
            f"{HALLUCINATION_GUARD}\n"
            "If the answer is unsupported, explicitly say the detail is not present in the retrieved context."
        ),
        design_decisions=[
            "The hallucination guard uses direct negative wording so the model gets a clear boundary against fabrication.",
            "The instruction to explicitly say a detail is missing prevents the model from filling gaps with plausible but unsupported facts.",
            "Repeating the retrieved-context requirement reinforces that absence of evidence should produce uncertainty, not invention.",
        ],
        lessons_learned=[
            "Models respond more reliably to explicit fallback language than to generic warnings about hallucination.",
            "Missing-information phrasing needs to be concrete and repeatable to pass edge cases consistently.",
        ],
    ),
    "surface_3": PromptSurfaceMetadata(
        surface_name="Context injection",
        winning_iteration="v5-template",
        pass_rate="pending empirical run",
        recorded_on=str(date.today()),
        focus="Provide listings in stable numbered format with normalized fields.",
        final_prompt=(
            RETRIEVAL_PROMPT_TEMPLATE + "\n\n"
            "Present retrieved listings in numbered order with normalized fields for price, rooms, bedrooms, bathrooms, location, condition, and description."
        ),
        design_decisions=[
            "A stable numbered context layout makes it easier for the model to trace facts back to specific listings.",
            "Normalized property fields reduce ambiguity caused by inconsistent wording across retrieved documents.",
            "Separating system prompt, context block, and query helps the model distinguish evidence from user intent.",
        ],
        lessons_learned=[
            "Structured context formatting is more reliable than raw document dumps.",
            "Field normalization improves consistency in comparisons and summaries.",
        ],
    ),
    "surface_4": PromptSurfaceMetadata(
        surface_name="Output format",
        winning_iteration="v5-template",
        pass_rate="pending empirical run",
        recorded_on=str(date.today()),
        focus="Constrain output into a short, reviewable structure.",
        final_prompt=(
            f"{SYSTEM_PROMPT}\n\n"
            f"{OUTPUT_FORMAT_INSTRUCTION}\n"
            "Keep each section concise and evidence-driven."
        ),
        design_decisions=[
            "The two-section structure creates a predictable response shape for manual review and automated keyword checks.",
            "Concise wording reduces the model's tendency to add decorative text that does not improve accuracy.",
            "Separating matches from insight makes it easier to see where evidence ends and synthesis begins.",
        ],
        lessons_learned=[
            "Explicit section titles are followed more reliably than abstract formatting guidance.",
            "Reviewability improves when the format is short and strongly constrained.",
        ],
    ),
    "surface_5": PromptSurfaceMetadata(
        surface_name="Relevance filtering",
        winning_iteration="v5-template",
        pass_rate="pending empirical run",
        recorded_on=str(date.today()),
        focus="Bias the model toward facts that align with the user query.",
        final_prompt=(
            f"{SYSTEM_PROMPT}\n\n"
            f"{RELEVANCE_FILTER_INSTRUCTION}\n"
            f"{CITATION_INSTRUCTION}"
        ),
        design_decisions=[
            "The relevance filter explicitly prioritizes location, room count, condition, and price because those are the strongest comparison axes in the dataset.",
            "Telling the model to ignore clearly unrelated facts reduces contamination from weaker retrieval matches.",
            "Combining relevance guidance with citation rules helps ensure that selected evidence remains inspectable.",
        ],
        lessons_learned=[
            "Relevance improves when the model is told which comparison fields matter most.",
            "Ignoring unrelated context needs to be stated directly rather than implied.",
        ],
    ),
}
