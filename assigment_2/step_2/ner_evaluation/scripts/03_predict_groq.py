"""
Prediction script for Model 3: Llama 3.3 70B via the Groq API.

This is an LLM-based approach. Unlike the token-classification models
(01, 02), the entities are extracted by prompting a general-purpose LLM in
natural language and asking it to return JSON. This replicates the approach
shown by the lecturer in Session 11 (slides 19-20), where Llama is queried
via Groq.

The prompt is defined in prompt_ner.py and is SHARED with the HuggingFace
Inference script (04), so that the LLM-vs-LLM comparison measures the model,
not the prompt.

Requires a GROQ_API_KEY in a local .env file (see .env.example).

Output: predictions/groq.json

Run from the ner_evaluation/ directory:
    poetry run python scripts/03_predict_groq.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv  # type: ignore
from groq import Groq  # type: ignore

from prompt_ner import SYSTEM_PROMPT, build_user_message
from utils import (
    CATEGORIES,
    build_predictions_output,
    get_gold_documents,
    load_gold_standard,
    save_predictions,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL_NAME: str = "llama-3.3-70b-versatile"
OUTPUT_FILENAME: str = "groq.json"

# temperature=0 makes the output as deterministic as the API allows.
# This is important for reproducibility (an explicit concern raised in the
# lecturer's slide 18: "you may not obtain the same results twice").
TEMPERATURE: float = 0.0

# Small pause between API calls to stay comfortably within free-tier limits.
SLEEP_BETWEEN_CALLS_SEC: float = 1.0


# ---------------------------------------------------------------------------
# LLM response parsing
# ---------------------------------------------------------------------------

def parse_llm_json(raw_content: str) -> dict[str, list[str]]:
    """Parse the LLM's JSON response into our 3-category schema.

    Defensive parsing:
        - Strips markdown fences if the model added them despite instructions.
        - Ensures all three keys (PER, ORG, PROJ) exist.
        - Ensures every value is a list of strings.

    Raises:
        ValueError: If the content cannot be parsed as the expected JSON.
    """
    cleaned = raw_content.strip()

    # Remove markdown code fences if present (```json ... ``` or ``` ... ```).
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Drop the first line (``` or ```json) and a trailing fence if any.
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM response is not valid JSON. Raw content:\n{raw_content}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object, got {type(data).__name__}")

    # Normalize: ensure all categories exist and contain lists of strings.
    result: dict[str, list[str]] = {}
    for cat in CATEGORIES:
        value = data.get(cat, [])
        if not isinstance(value, list):
            raise ValueError(f"Category '{cat}' is not a list: {value!r}")
        result[cat] = [str(item).strip() for item in value if str(item).strip()]

    return result


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def predict_one(client: Groq, text: str) -> dict[str, list[str]]:
    """Send one acknowledgement text to the LLM and parse the result."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(text)},
        ],
        temperature=TEMPERATURE,
        response_format={"type": "json_object"},
    )
    raw_content = response.choices[0].message.content
    return parse_llm_json(raw_content)


def main() -> None:
    # Load environment variables from .env in the ner_evaluation/ directory.
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.startswith("gsk_your"):
        print("ERROR: GROQ_API_KEY not found or still set to the placeholder.")
        print(f"  Create a .env file at {env_path} with a real key.")
        sys.exit(1)

    print("Loading gold standard...")
    gold = load_gold_standard()
    documents = get_gold_documents(gold)
    print(f"  Loaded {len(documents)} documents.")

    print(f"Initializing Groq client (model: {MODEL_NAME})")
    client = Groq(api_key=api_key)

    print(f"Running inference on {len(documents)} documents...")
    predictions: list[dict] = []
    for i, doc in enumerate(documents):
        paper_id = doc["paper_id"]
        text = doc["text"]
        try:
            entities = predict_one(client, text)
        except ValueError as exc:
            # If a single document fails to parse, record it as empty rather
            # than crashing the whole run. The evaluation will count this as
            # missed entities (false negatives).
            print(f"  {paper_id}: PARSE ERROR -> {exc}")
            entities = {cat: [] for cat in CATEGORIES}

        predictions.append({
            "paper_id": paper_id,
            "text": text,
            "entities": entities,
        })
        print(f"  {paper_id}: "
              f"PER={len(entities['PER'])}, "
              f"ORG={len(entities['ORG'])}, "
              f"PROJ={len(entities['PROJ'])}")

        # Pause between calls (skip after the last one).
        if i < len(documents) - 1:
            time.sleep(SLEEP_BETWEEN_CALLS_SEC)

    output = build_predictions_output(
        model_name=f"groq/{MODEL_NAME}",
        model_parameters={
            "provider": "Groq",
            "model": MODEL_NAME,
            "temperature": TEMPERATURE,
            "response_format": "json_object",
            "prompt": "shared one-shot prompt (see prompt_ner.py)",
        },
        documents_predictions=predictions,
        notes=(
            "LLM-based extraction via the Groq API, replicating the approach "
            "shown in Session 11 (slides 19-20). Uses a shared one-shot prompt "
            "(prompt_ner.py) encoding the gold-standard annotation rules. "
            "temperature=0 for maximum determinism; note that LLM output is "
            "still not guaranteed to be fully reproducible."
        ),
    )

    out_path = save_predictions(output, OUTPUT_FILENAME)
    print(f"Predictions written to: {out_path}")


if __name__ == "__main__":
    main()
