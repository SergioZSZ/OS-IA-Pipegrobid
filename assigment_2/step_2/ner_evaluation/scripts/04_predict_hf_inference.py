"""
Prediction script for Model 4: Qwen2.5-7B-Instruct via HuggingFace Inference.

This is the second LLM-based approach. It uses the HuggingFace Inference
Providers service (via the InferenceClient), which serves open-source models
hosted on the HuggingFace Hub. This directly satisfies the assignment
requirement to "use HuggingFace as an open platform for ML models".

It deliberately uses a model from a DIFFERENT family than the Groq model
(Qwen vs Llama), so the LLM-vs-LLM comparison is informative across model
families, not just across providers.

The prompt is the SAME shared one-shot prompt used by the Groq script
(prompt_ner.py), so the comparison measures the model, not the prompt.

Requires an HF_TOKEN in a local .env file (see .env.example).

Output: predictions/hf_inference.json

Run from the ner_evaluation/ directory:
    poetry run python scripts/04_predict_hf_inference.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv  # type: ignore
from huggingface_hub import InferenceClient  # type: ignore

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

# Primary model. If HF Inference does not serve this exact model at runtime,
# the script will fail with a clear message; switch to the fallback below.
MODEL_NAME: str = "Qwen/Qwen2.5-7B-Instruct"
# Fallback option (uncomment / swap if the primary is unavailable):
# MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"

OUTPUT_FILENAME: str = "hf_inference.json"

# temperature=0 for maximum determinism (same rationale as the Groq script).
TEMPERATURE: float = 0.0

# Max tokens for the model's JSON answer. Acknowledgements are short, but
# paper_28 has ~25 entities, so we leave generous headroom.
MAX_TOKENS: int = 1024

# Pause between API calls to stay within free-tier limits.
SLEEP_BETWEEN_CALLS_SEC: float = 2.0


# ---------------------------------------------------------------------------
# LLM response parsing
# ---------------------------------------------------------------------------

def parse_llm_json(raw_content: str) -> dict[str, list[str]]:
    """Parse the LLM's JSON response into our 3-category schema.

    Identical defensive logic to the Groq script: strips markdown fences,
    ensures all three categories exist, ensures values are lists of strings.

    Raises:
        ValueError: If the content cannot be parsed as the expected JSON.
    """
    cleaned = raw_content.strip()

    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
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

def predict_one(client: InferenceClient, text: str) -> dict[str, list[str]]:
    """Send one acknowledgement text to the LLM and parse the result."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_message(text)},
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        response_format={"type": "json_object"},
    )
    raw_content = response.choices[0].message.content
    return parse_llm_json(raw_content)


def main() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)

    hf_token = os.getenv("HF_TOKEN")
    if not hf_token or hf_token.startswith("hf_lo_ponemos"):
        print("ERROR: HF_TOKEN not found or still set to the placeholder.")
        print(f"  Create a .env file at {env_path} with a real HF token.")
        sys.exit(1)

    print("Loading gold standard...")
    gold = load_gold_standard()
    documents = get_gold_documents(gold)
    print(f"  Loaded {len(documents)} documents.")

    print(f"Initializing HuggingFace InferenceClient (model: {MODEL_NAME})")
    client = InferenceClient(token=hf_token)

    print(f"Running inference on {len(documents)} documents...")
    predictions: list[dict] = []
    for i, doc in enumerate(documents):
        paper_id = doc["paper_id"]
        text = doc["text"]
        try:
            entities = predict_one(client, text)
        except ValueError as exc:
            print(f"  {paper_id}: PARSE ERROR -> {exc}")
            entities = {cat: [] for cat in CATEGORIES}
        except Exception as exc:  # noqa: BLE001
            # Network / availability / auth errors: report clearly and stop,
            # because if one call fails for these reasons, all will.
            print(f"  {paper_id}: API ERROR -> {type(exc).__name__}: {exc}")
            print("  Aborting. Check model availability or HF_TOKEN.")
            sys.exit(1)

        predictions.append({
            "paper_id": paper_id,
            "text": text,
            "entities": entities,
        })
        print(f"  {paper_id}: "
              f"PER={len(entities['PER'])}, "
              f"ORG={len(entities['ORG'])}, "
              f"PROJ={len(entities['PROJ'])}")

        if i < len(documents) - 1:
            time.sleep(SLEEP_BETWEEN_CALLS_SEC)

    output = build_predictions_output(
        model_name=f"hf/{MODEL_NAME}",
        model_parameters={
            "provider": "HuggingFace Inference Providers",
            "model": MODEL_NAME,
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
            "response_format": "json_object",
            "prompt": "shared one-shot prompt (see prompt_ner.py)",
        },
        documents_predictions=predictions,
        notes=(
            "LLM-based extraction via HuggingFace Inference Providers. Uses "
            "the same shared one-shot prompt as the Groq script (prompt_ner.py) "
            "so the LLM-vs-LLM comparison isolates the model. Qwen2.5 belongs "
            "to a different model family than the Llama model used via Groq, "
            "making the cross-family comparison meaningful. temperature=0 for "
            "maximum determinism; LLM output is still not fully reproducible."
        ),
    )

    out_path = save_predictions(output, OUTPUT_FILENAME)
    print(f"Predictions written to: {out_path}")


if __name__ == "__main__":
    main()
