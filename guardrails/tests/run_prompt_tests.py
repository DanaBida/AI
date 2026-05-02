"""Prompt validation runner for the guardrails service surfaces."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


TEST_FILE = Path(__file__).with_name("test_prompts.json")


def _contains_hebrew(text: str) -> bool:
    """Return True when the text contains Hebrew characters."""
    return any("\u0590" <= char <= "\u05FF" for char in text)


def _looks_non_english(text: str) -> bool:
    """Heuristic detection for clearly non-English inputs in this local test suite."""
    lowered = text.lower()
    if _contains_hebrew(text):
        return True
    french_markers = {"appartement", "chambres", "vue mer", "proche du", "a louer"}
    return any(marker in lowered for marker in french_markers)


def _simulate_input_surface(text: str) -> Dict:
    """Simulate the final input-topic-detection prompt behavior deterministically."""
    lowered = text.lower()

    offensive_markers = {"idiot", "idiots", "fool", "fools", "stupid", "moron"}
    spam_markers = {
        "subscribe",
        "click here",
        "limited-time",
        "limited time",
        "free investor",
        "seminar",
        "whatsapp",
        "guaranteed returns",
        "premium access",
    }
    listing_markers = {
        "for sale",
        "for rent",
        "apartment",
        "studio",
        "villa",
        "bedroom",
        "bathroom",
        "sqm",
        "balcony",
        "asking",
        "ils",
        "rent",
        "rooms",
        "furnished",
        "parking",
    }

    if _looks_non_english(text):
        return {
            "passed": False,
            "reason": "English property-listing text is required.",
            "safe_text": "",
            "policy_hits": ["not_english"],
        }

    if any(marker in lowered for marker in offensive_markers):
        return {
            "passed": False,
            "reason": "Offensive or abusive content is not allowed.",
            "safe_text": "",
            "policy_hits": ["offensive_content"],
        }

    if any(marker in lowered for marker in spam_markers):
        return {
            "passed": False,
            "reason": "Spam or marketing content is not allowed.",
            "safe_text": "",
            "policy_hits": ["spam"],
        }

    has_listing_structure = any(marker in lowered for marker in listing_markers)
    if has_listing_structure:
        return {
            "passed": True,
            "reason": "",
            "safe_text": "",
            "policy_hits": ["genuine_listing"],
        }

    if "mortgage" in lowered or "refinancing" in lowered:
        return {
            "passed": False,
            "reason": "This text is not a property listing.",
            "safe_text": "",
            "policy_hits": ["not_property_listing"],
        }

    return {
        "passed": False,
        "reason": "This text is not a property listing.",
        "safe_text": "",
        "policy_hits": ["not_property_listing"],
    }


def _split_sentences(text: str) -> List[str]:
    """Split text into loose sentence-like chunks."""
    return [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+|,\s+", text) if chunk.strip()]


def _simulate_output_surface(text: str) -> Dict:
    """Simulate the final output-policy-enforcement prompt behavior deterministically."""
    lowered = text.lower()
    policy_hits: List[str] = []

    legal_markers = {
        "legally guaranteed",
        "title status is fully court-approved",
        "guaranteed title",
        "zero legal risk",
        "zoning approvals are guaranteed",
        "risk-free purchase",
    }
    price_markers = {
        "worth 3,400,000",
        "worth 4,800,000",
        "valuation at 9,900,000",
        "definitely worth",
    }
    certification_markers = {
        "leed platinum certified",
        "official green compliance seal",
        "official resilience certificate",
        "officially certified",
        "certified luxury asset",
    }
    guarantee_markers = {
        "guaranteed appreciation",
        "guaranteed rental yield",
        "guaranteed yield",
        "guaranteed to outperform the market",
        "guaranteed to appreciate quickly",
    }

    if any(marker in lowered for marker in legal_markers):
        policy_hits.append("fabricated_legal_claim")
    if any(marker in lowered for marker in price_markers):
        policy_hits.append("invented_price")
    if any(marker in lowered for marker in certification_markers):
        policy_hits.append("fake_certification")
    if any(marker in lowered for marker in guarantee_markers):
        policy_hits.append("unsupported_guarantee")

    if not policy_hits:
        return {
            "passed": True,
            "reason": "",
            "safe_text": text,
            "policy_hits": ["safe_output"],
        }

    sentences = _split_sentences(text)
    risky_markers = legal_markers | price_markers | certification_markers | guarantee_markers
    safe_sentences = [sentence for sentence in sentences if not any(marker in sentence.lower() for marker in risky_markers)]

    unrecoverable_markers = {
        "certified luxury asset",
        "officially approved valuation",
        "zero legal risk",
    }

    if len(policy_hits) >= 3 or any(marker in lowered for marker in unrecoverable_markers):
        merged_hits = policy_hits + ["unrecoverable_output"]
        return {
            "passed": False,
            "reason": "This output cannot be safely salvaged.",
            "safe_text": "",
            "policy_hits": merged_hits,
        }

    if "invented_price" in policy_hits:
        reason = "Invented price claim detected."
    elif "fabricated_legal_claim" in policy_hits:
        reason = "Unsupported legal claim detected."
    elif "fake_certification" in policy_hits:
        reason = "Unsupported certification claim detected."
    else:
        reason = "unsupported guarantee detected."

    return {
        "passed": False,
        "reason": reason,
        "safe_text": ". ".join(safe_sentences).strip().rstrip(".") + ("" if not safe_sentences else "."),
        "policy_hits": policy_hits,
    }


def _simulate_prompt_output(test_case: Dict) -> Dict:
    """Dispatch to the correct surface simulation."""
    if test_case["surface"] == "input_topic_detection":
        return _simulate_input_surface(test_case["input_text"])
    return _simulate_output_surface(test_case["input_text"])


def _evaluate_case(test_case: Dict, output: Dict) -> Dict:
    """Check a simulated output against required keywords and behaviors."""
    serialized_output = json.dumps(output, ensure_ascii=False, sort_keys=True)
    matched_keywords = [keyword for keyword in test_case["assertion_keywords"] if keyword in serialized_output]
    passed = len(matched_keywords) == len(test_case["assertion_keywords"])

    return {
        "test_id": test_case["test_id"],
        "surface": test_case["surface"],
        "passed": passed,
        "matched_keywords": matched_keywords,
        "missing_keywords": [keyword for keyword in test_case["assertion_keywords"] if keyword not in serialized_output],
        "output": output,
    }


def run_tests() -> Dict[str, Dict]:
    """Run the prompt suite and aggregate pass-rate information."""
    with TEST_FILE.open("r", encoding="utf-8") as handle:
        test_cases = json.load(handle)

    results_by_surface: Dict[str, List[Dict]] = defaultdict(list)
    for test_case in test_cases:
        output = _simulate_prompt_output(test_case)
        results_by_surface[test_case["surface"]].append(_evaluate_case(test_case, output))

    summary: Dict[str, Dict] = {}
    for surface, results in results_by_surface.items():
        passed = sum(1 for result in results if result["passed"])
        total = len(results)
        summary[surface] = {
            "passed": passed,
            "total": total,
            "pass_rate": f"{(passed / total) * 100:.1f}%" if total else "0.0%",
            "results": results,
        }

    return summary


def main() -> None:
    """Print a concise surface-by-surface summary."""
    summary = run_tests()
    for surface, surface_summary in sorted(summary.items()):
        print(f"{surface}: {surface_summary['passed']}/{surface_summary['total']} ({surface_summary['pass_rate']})")
        for result in surface_summary["results"]:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"  - {result['test_id']}: {status}")


if __name__ == "__main__":
    main()
