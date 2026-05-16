"""
Shared utilities for the NER evaluation pipeline.

This module provides:
    - Path constants pointing to the gold standard, predictions, and reports.
    - Loading helpers for the gold standard JSON.
    - Entity normalization for fair string matching during evaluation.
    - A common output format builder for prediction scripts.

All prediction scripts (01-04) and the evaluation script (05) import from here
to ensure a single source of truth for matching policy and I/O formats.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# This file lives at:
#   <repo_root>/assigment_2/step_2/ner_evaluation/scripts/utils.py
# So we go up four levels to reach <repo_root>.

REPO_ROOT: Path = Path(__file__).resolve().parents[4]

GOLD_STANDARD_PATH: Path = REPO_ROOT / "corpus" / "gold_standard.json"

NER_EVAL_ROOT: Path = REPO_ROOT / "assigment_2" / "step_2" / "ner_evaluation"
PREDICTIONS_DIR: Path = NER_EVAL_ROOT / "predictions"
REPORTS_DIR: Path = NER_EVAL_ROOT / "reports"


# ---------------------------------------------------------------------------
# Entity categories
# ---------------------------------------------------------------------------

CATEGORIES: tuple[str, ...] = ("PER", "ORG", "PROJ")


# ---------------------------------------------------------------------------
# Gold standard I/O
# ---------------------------------------------------------------------------

def load_gold_standard(path: Path = GOLD_STANDARD_PATH) -> dict[str, Any]:
    """Load the gold standard JSON file.

    Returns the full parsed dictionary with keys 'metadata' and 'documents'.

    Raises:
        FileNotFoundError: If the gold standard file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Gold standard not found at {path}. "
            f"Expected location: <repo_root>/corpus/gold_standard.json"
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_gold_documents(gold: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the list of annotated documents from a loaded gold standard."""
    return gold["documents"]


# ---------------------------------------------------------------------------
# Entity normalization (matching policy: light normalization)
# ---------------------------------------------------------------------------

# Regex to collapse multiple whitespace characters (spaces, tabs, newlines)
# into a single space.
_WHITESPACE_RE = re.compile(r"\s+")

# Regex to normalize hyphens with INCONSISTENT surrounding whitespace.
# It only matches a hyphen that has whitespace on exactly one side, e.g.:
#   "Department of Health -Epidemiology Bureau"   (space before, none after)
#   "Department of Health- Epidemiology Bureau"   (none before, space after)
# These are annotation/extraction artifacts and get normalized to " - ".
#
# It deliberately does NOT match hyphens with consistent spacing:
#   "SARS-CoV-2"          (no space either side) -> left untouched
#   "EP/S023356/1"        (no space either side) -> left untouched
#   "Health - Epidemiology" (space both sides)   -> left untouched
#
# The two alternatives in the pattern are:
#   \s+-(?!\s)   ->  whitespace, hyphen, NOT followed by whitespace
#   (?<!\s)-\s+  ->  hyphen NOT preceded by whitespace, then whitespace
_HYPHEN_RE = re.compile(r"\s+-(?!\s)|(?<!\s)-\s+")


def normalize_entity(entity: str) -> str:
    """Apply light normalization for fair string matching.

    Applied transformations (in order):
        1. Strip leading and trailing whitespace.
        2. Collapse runs of internal whitespace into a single space.
        3. Fix hyphens with inconsistent surrounding whitespace, normalizing
           them to ' - '. Hyphens with consistent spacing (none on either
           side, or a space on both sides) are left untouched. This protects
           legitimate hyphenated names and codes such as 'SARS-CoV-2' or
           'EP/S023356/1' from being mangled.

    Case is preserved (NER is case-sensitive: 'NEI' != 'nei').
    Punctuation other than hyphens is preserved.

    This implements matching policy (b) agreed upon for evaluation.
    """
    if not isinstance(entity, str):
        raise TypeError(f"Expected str, got {type(entity).__name__}")
    s = entity.strip()
    s = _WHITESPACE_RE.sub(" ", s)
    s = _HYPHEN_RE.sub(" - ", s)
    # The hyphen substitution may have introduced double spaces; collapse
    # internal whitespace once more to be safe.
    s = _WHITESPACE_RE.sub(" ", s)
    return s


def normalize_entity_set(entities: list[str]) -> set[str]:
    """Normalize a list of entities and return them as a set.

    Duplicates after normalization are silently collapsed (which is the
    desired behavior for set-based evaluation).
    """
    return {normalize_entity(e) for e in entities}


# ---------------------------------------------------------------------------
# Prediction output formatting
# ---------------------------------------------------------------------------

def build_predictions_output(
    model_name: str,
    model_parameters: dict[str, Any],
    documents_predictions: list[dict[str, Any]],
    notes: str | None = None,
) -> dict[str, Any]:
    """Build the standardized output dictionary written by prediction scripts.

    The returned dict has the same shape as the gold standard, plus a
    'metadata' block describing how the predictions were generated. This
    allows the evaluation script to compare them apples-to-apples.

    Args:
        model_name: Unique identifier of the model (e.g. 'kalawinka/flair-...').
        model_parameters: Inference parameters (temperature, mapping, etc.).
        documents_predictions: List of dicts, one per document, each with
            keys 'paper_id', 'text', and 'entities' (a dict with PER, ORG,
            PROJ lists).
        notes: Optional free-text notes about this run.
    """
    return {
        "metadata": {
            "model_name": model_name,
            "model_parameters": model_parameters,
            "execution_date": datetime.now(timezone.utc).isoformat(),
            "categories": list(CATEGORIES),
            "notes": notes,
        },
        "documents": documents_predictions,
    }


def save_predictions(predictions: dict[str, Any], filename: str) -> Path:
    """Save predictions to PREDICTIONS_DIR / filename and return the path."""
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PREDICTIONS_DIR / filename
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)
    return out_path
