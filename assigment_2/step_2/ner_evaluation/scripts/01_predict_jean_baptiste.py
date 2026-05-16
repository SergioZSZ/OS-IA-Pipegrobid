"""
Prediction script for Model 1: Jean-Baptiste/roberta-large-ner-english.

This is the model shown by the lecturer in Session 11 (slide 22) as the
canonical NER example. We include it as a narrative baseline:
    - It is a classic transformer-based token classifier.
    - It detects PER, ORG, LOC and MISC out of the box.
    - It does NOT detect grant codes (PROJ), which is why we later move to
      domain-specialized and LLM-based approaches.

Output: predictions/jean_baptiste.json with the standard format defined in
utils.build_predictions_output.

Run from the ner_evaluation/ directory:
    poetry run python scripts/01_predict_jean_baptiste.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make sibling 'utils' importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from transformers import pipeline  # type: ignore

from utils import (
    build_predictions_output,
    get_gold_documents,
    load_gold_standard,
    save_predictions,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME: str = "Jean-Baptiste/roberta-large-ner-english"
OUTPUT_FILENAME: str = "jean_baptiste.json"

# This model emits 4 labels: PER, ORG, LOC, MISC.
# We map them to our 3-category schema. Labels not in this dict are dropped.
#   - LOC: we do not annotate geographic locations in our gold standard.
#   - MISC: catch-all category, not aligned with any of our three.
# PROJ has no source label here — this model is unable to detect grant codes,
# so we always emit an empty list for that category.
LABEL_MAPPING: dict[str, str] = {
    "PER": "PER",
    "ORG": "ORG",
}

# aggregation_strategy="simple" merges adjacent subword tokens with the same
# label into a single entity span. Without it, the model returns one entry per
# subword (e.g. 'Nat', '##ional', '##Sc', ...), which is unusable here.
AGGREGATION_STRATEGY: str = "simple"


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def predict_one(ner_pipeline, text: str) -> dict[str, list[str]]:
    """Run the NER pipeline on a single text and map outputs to our schema.

    Returns a dict with keys PER, ORG, PROJ. PROJ is always an empty list
    because this model has no PROJ-equivalent label.

    Duplicates within a single text are preserved as a list (downstream
    evaluation will set-ify them).
    """
    entities: dict[str, list[str]] = {"PER": [], "ORG": [], "PROJ": []}

    raw_results = ner_pipeline(text)

    for span in raw_results:
        src_label = span["entity_group"]
        if src_label not in LABEL_MAPPING:
            continue
        target_label = LABEL_MAPPING[src_label]
        # The 'word' field can include a leading space from the tokenizer.
        # We strip it; further normalization happens at evaluation time.
        text_span = span["word"].strip()
        if text_span:
            entities[target_label].append(text_span)

    return entities


def main() -> None:
    print(f"Loading gold standard...")
    gold = load_gold_standard()
    documents = get_gold_documents(gold)
    print(f"  Loaded {len(documents)} documents.")

    print(f"Loading model: {MODEL_NAME}")
    print(f"  (First run downloads ~1.4 GB. Subsequent runs use local cache.)")
    ner_pipeline = pipeline(
        task="ner",
        model=MODEL_NAME,
        aggregation_strategy=AGGREGATION_STRATEGY,
    )
    print(f"  Model loaded.")

    print(f"Running inference on {len(documents)} documents...")
    predictions: list[dict] = []
    for doc in documents:
        paper_id = doc["paper_id"]
        text = doc["text"]
        entities = predict_one(ner_pipeline, text)
        predictions.append({
            "paper_id": paper_id,
            "text": text,
            "entities": entities,
        })
        print(f"  {paper_id}: "
              f"PER={len(entities['PER'])}, "
              f"ORG={len(entities['ORG'])}, "
              f"PROJ={len(entities['PROJ'])}")

    output = build_predictions_output(
        model_name=MODEL_NAME,
        model_parameters={
            "aggregation_strategy": AGGREGATION_STRATEGY,
            "label_mapping": LABEL_MAPPING,
            "proj_supported_natively": False,
        },
        documents_predictions=predictions,
        notes=(
            "Lecturer's example model from Session 11 (slide 22). "
            "Included as narrative baseline. Native labels PER/ORG/LOC/MISC; "
            "LOC and MISC are dropped during mapping. PROJ is not supported "
            "natively by this model and always returns an empty list."
        ),
    )

    out_path = save_predictions(output, OUTPUT_FILENAME)
    print(f"Predictions written to: {out_path}")


if __name__ == "__main__":
    main()
