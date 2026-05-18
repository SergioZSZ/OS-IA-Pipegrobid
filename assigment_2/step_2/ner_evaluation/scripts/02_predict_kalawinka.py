"""
Prediction script for Model 2: kalawinka/flair-ner-acknowledgments.

This model is a Flair-based sequence tagger trained specifically on the
acknowledgement sections of scientific papers (Smirnova & Mayr, GESIS;
arXiv:2307.13377). Unlike a generic NER model, its label set is tailored to
this exact domain.

The model emits 6 labels. We map them to our 3-category schema:
    IND  (individuals)      -> PER
    UNI  (universities)     -> ORG
    FUND (funding agencies) -> ORG
    COR  (corporations)     -> ORG
    GRNB (grant numbers)    -> PROJ
    MISC (miscellaneous)    -> dropped (not aligned with our schema)

This is the only model in the comparison that detects PROJ-equivalent
entities natively, which is why we expect it to outperform the generic
baseline (Jean-Baptiste) on our task.

NOTE ON COMPATIBILITY:
This model was serialized with an older PyTorch format. PyTorch >= 2.6 changed
the default of torch.load to weights_only=True, which rejects this file. We
explicitly load it with weights_only=False. This is safe here because the
model comes from a known academic repository (the authors of the GESIS paper),
not from an untrusted source.

Output: predictions/kalawinka.json

Run from the ner_evaluation/ directory:
    poetry run python scripts/02_predict_kalawinka.py
"""

from __future__ import annotations

import functools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import torch  # type: ignore

# --- PyTorch >= 2.6 compatibility patch for Flair model loading -------------
# Force weights_only=False so that Flair can deserialize this model.
# We wrap the original torch.load and inject the argument.
_original_torch_load = torch.load


@functools.wraps(_original_torch_load)
def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _original_torch_load(*args, **kwargs)


torch.load = _patched_torch_load
# ----------------------------------------------------------------------------

from flair.data import Sentence  # type: ignore  # noqa: E402
from flair.models import SequenceTagger  # type: ignore  # noqa: E402

from utils import (  # noqa: E402
    build_predictions_output,
    get_gold_documents,
    load_gold_standard,
    save_predictions,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME: str = "kalawinka/flair-ner-acknowledgments"
OUTPUT_FILENAME: str = "kalawinka.json"

# Map the model's 6 native labels onto our 3-category schema.
# Labels not present in this dict (i.e. MISC) are dropped.
LABEL_MAPPING: dict[str, str] = {
    "IND": "PER",    # individuals
    "UNI": "ORG",    # universities
    "FUND": "ORG",   # funding agencies
    "COR": "ORG",    # corporations
    "GRNB": "PROJ",  # grant numbers
    # "MISC" intentionally omitted -> dropped
}


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def predict_one(tagger: SequenceTagger, text: str) -> dict[str, list[str]]:
    """Run the Flair tagger on a single text and map outputs to our schema.

    Returns a dict with keys PER, ORG, PROJ.

    Duplicates within a single text are preserved as a list (downstream
    evaluation will set-ify them).
    """
    entities: dict[str, list[str]] = {"PER": [], "ORG": [], "PROJ": []}

    sentence = Sentence(text)
    tagger.predict(sentence)

    for span in sentence.get_spans("ner"):
        # In Flair, span.tag is the predicted label, span.text is the surface
        # string of the entity span.
        src_label = span.tag
        if src_label not in LABEL_MAPPING:
            continue
        target_label = LABEL_MAPPING[src_label]
        text_span = span.text.strip()
        if text_span:
            entities[target_label].append(text_span)

    return entities


def main() -> None:
    print("Loading gold standard...")
    gold = load_gold_standard()
    documents = get_gold_documents(gold)
    print(f"  Loaded {len(documents)} documents.")

    print(f"Loading model: {MODEL_NAME}")
    print("  (Using cached model if already downloaded.)")
    tagger = SequenceTagger.load(MODEL_NAME)
    print("  Model loaded.")

    print(f"Running inference on {len(documents)} documents...")
    predictions: list[dict] = []
    for doc in documents:
        paper_id = doc["paper_id"]
        text = doc["text"]
        entities = predict_one(tagger, text)
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
            "framework": "flair",
            "label_mapping": LABEL_MAPPING,
            "dropped_labels": ["MISC"],
            "proj_supported_natively": True,
            "torch_load_weights_only": False,
        },
        documents_predictions=predictions,
        notes=(
            "Domain-specialized NER model trained on scientific "
            "acknowledgements (Smirnova & Mayr, arXiv:2307.13377). "
            "Native labels IND/UNI/FUND/COR/GRNB/MISC mapped to PER/ORG/PROJ; "
            "MISC is dropped. Unlike the generic baseline, this model detects "
            "grant numbers (GRNB -> PROJ) natively. Loaded with "
            "weights_only=False for PyTorch >= 2.6 compatibility."
        ),
    )

    out_path = save_predictions(output, OUTPUT_FILENAME)
    print(f"Predictions written to: {out_path}")


if __name__ == "__main__":
    main()
