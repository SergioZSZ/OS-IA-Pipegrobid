"""
Evaluation script: compares model predictions against the gold standard.

For each model and each category (PER, ORG, PROJ), it computes:
    - True Positives (TP):  entities present in both prediction and gold
    - False Positives (FP): entities predicted but not in gold
    - False Negatives (FN): entities in gold but not predicted
    - Precision, Recall, F1 (micro-averaged over the 8 documents)

Matching policy: set-based comparison after light normalization
(see utils.normalize_entity). Case-sensitive.

Inputs:
    - corpus/gold_standard.json
    - predictions/*.json  (one file per model; whichever are present)

Outputs:
    - reports/evaluation_report.json  (structured metrics + per-paper detail)
    - reports/evaluation_report.md    (human-readable comparative report)

Run from the ner_evaluation/ directory:
    poetry run python scripts/05_evaluate.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import (
    CATEGORIES,
    PREDICTIONS_DIR,
    REPORTS_DIR,
    get_gold_documents,
    load_gold_standard,
    normalize_entity_set,
)


# ---------------------------------------------------------------------------
# Core metric computation
# ---------------------------------------------------------------------------

def compute_confusion(gold: list[str], pred: list[str]) -> dict[str, Any]:
    """Compare a gold list and a predicted list of entity strings.

    Both lists are normalized and turned into sets before comparison.

    Returns a dict with TP/FP/FN counts and the actual entity strings in
    each bucket (useful for qualitative error analysis later).
    """
    gold_set = normalize_entity_set(gold)
    pred_set = normalize_entity_set(pred)

    tp_set = gold_set & pred_set
    fp_set = pred_set - gold_set
    fn_set = gold_set - pred_set

    return {
        "tp": len(tp_set),
        "fp": len(fp_set),
        "fn": len(fn_set),
        "tp_entities": sorted(tp_set),
        "fp_entities": sorted(fp_set),
        "fn_entities": sorted(fn_set),
    }


def precision_recall_f1(tp: int, fp: int, fn: int) -> dict[str, float]:
    """Compute precision, recall and F1 from raw counts.

    Edge cases (following the standard convention):
        - If TP+FP == 0 (no predictions): precision = 0.0
        - If TP+FN == 0 (no gold entities): recall = 0.0
        - If precision+recall == 0: F1 = 0.0
    """
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


# ---------------------------------------------------------------------------
# Per-model evaluation
# ---------------------------------------------------------------------------

def evaluate_model(
    gold_docs: list[dict[str, Any]],
    pred_docs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate one model's predictions against the gold standard.

    Returns a dict with:
        - 'per_category': micro-averaged P/R/F1 per category + total counts
        - 'overall': micro-averaged P/R/F1 across all categories combined
        - 'per_paper': per-paper, per-category confusion detail
    """
    # Index predictions by paper_id for safe lookup (order-independent).
    pred_by_id = {d["paper_id"]: d for d in pred_docs}

    # Accumulators for micro-averaging.
    cat_counts = {cat: {"tp": 0, "fp": 0, "fn": 0} for cat in CATEGORIES}
    per_paper: list[dict[str, Any]] = []

    for gold_doc in gold_docs:
        paper_id = gold_doc["paper_id"]
        pred_doc = pred_by_id.get(paper_id)

        if pred_doc is None:
            # The model produced no prediction for this paper: every gold
            # entity counts as a false negative.
            print(f"  WARNING: no prediction for {paper_id}; "
                  f"counting all gold entities as FN.")
            pred_entities = {cat: [] for cat in CATEGORIES}
        else:
            pred_entities = pred_doc["entities"]

        paper_detail: dict[str, Any] = {"paper_id": paper_id, "categories": {}}

        for cat in CATEGORIES:
            gold_list = gold_doc["entities"].get(cat, [])
            pred_list = pred_entities.get(cat, [])
            confusion = compute_confusion(gold_list, pred_list)

            cat_counts[cat]["tp"] += confusion["tp"]
            cat_counts[cat]["fp"] += confusion["fp"]
            cat_counts[cat]["fn"] += confusion["fn"]

            paper_detail["categories"][cat] = confusion

        per_paper.append(paper_detail)

    # Micro-averaged metrics per category.
    per_category: dict[str, Any] = {}
    for cat in CATEGORIES:
        counts = cat_counts[cat]
        metrics = precision_recall_f1(counts["tp"], counts["fp"], counts["fn"])
        per_category[cat] = {**counts, **metrics}

    # Overall micro-averaged metrics (all categories pooled together).
    total_tp = sum(cat_counts[c]["tp"] for c in CATEGORIES)
    total_fp = sum(cat_counts[c]["fp"] for c in CATEGORIES)
    total_fn = sum(cat_counts[c]["fn"] for c in CATEGORIES)
    overall = {
        "tp": total_tp,
        "fp": total_fp,
        "fn": total_fn,
        **precision_recall_f1(total_tp, total_fp, total_fn),
    }

    return {
        "per_category": per_category,
        "overall": overall,
        "per_paper": per_paper,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def discover_prediction_files() -> list[Path]:
    """Return all prediction JSON files currently present, sorted by name."""
    if not PREDICTIONS_DIR.exists():
        return []
    return sorted(PREDICTIONS_DIR.glob("*.json"))


def build_markdown_report(results: dict[str, dict[str, Any]]) -> str:
    """Build a human-readable Markdown comparative report."""
    lines: list[str] = []
    lines.append("# NER Model Evaluation Report")
    lines.append("")
    lines.append("Evaluation of NER models on the acknowledgements gold "
                 "standard (8 documents).")
    lines.append("")
    lines.append("Matching policy: set-based comparison after light "
                 "normalization (strip, whitespace collapse, hyphen "
                 "normalization). Case-sensitive. Metrics are micro-averaged "
                 "over the 8 documents.")
    lines.append("")

    # --- Comparative table: overall + per-category F1 ---
    lines.append("## Comparative summary (F1 per category)")
    lines.append("")
    lines.append("| Model | PER F1 | ORG F1 | PROJ F1 | Overall F1 |")
    lines.append("|---|---|---|---|---|")
    for model_name, res in results.items():
        pc = res["per_category"]
        lines.append(
            f"| {model_name} "
            f"| {pc['PER']['f1']:.4f} "
            f"| {pc['ORG']['f1']:.4f} "
            f"| {pc['PROJ']['f1']:.4f} "
            f"| {res['overall']['f1']:.4f} |"
        )
    lines.append("")

    # --- Detailed table per model ---
    lines.append("## Detailed metrics per model")
    lines.append("")
    for model_name, res in results.items():
        lines.append(f"### {model_name}")
        lines.append("")
        lines.append("| Category | TP | FP | FN | Precision | Recall | F1 |")
        lines.append("|---|---|---|---|---|---|---|")
        for cat in CATEGORIES:
            m = res["per_category"][cat]
            lines.append(
                f"| {cat} | {m['tp']} | {m['fp']} | {m['fn']} "
                f"| {m['precision']:.4f} | {m['recall']:.4f} "
                f"| {m['f1']:.4f} |"
            )
        o = res["overall"]
        lines.append(
            f"| **Overall** | {o['tp']} | {o['fp']} | {o['fn']} "
            f"| {o['precision']:.4f} | {o['recall']:.4f} "
            f"| {o['f1']:.4f} |"
        )
        lines.append("")

    # --- Winner ---
    if results:
        winner = max(results.items(), key=lambda kv: kv[1]["overall"]["f1"])
        lines.append("## Best model (by overall micro-averaged F1)")
        lines.append("")
        lines.append(f"**{winner[0]}** "
                     f"(Overall F1 = {winner[1]['overall']['f1']:.4f})")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    print("Loading gold standard...")
    gold = load_gold_standard()
    gold_docs = get_gold_documents(gold)
    print(f"  {len(gold_docs)} documents.")

    pred_files = discover_prediction_files()
    if not pred_files:
        print(f"No prediction files found in {PREDICTIONS_DIR}.")
        print("Run a prediction script (e.g. 01_predict_jean_baptiste.py) "
              "first.")
        sys.exit(1)

    print(f"Found {len(pred_files)} prediction file(s): "
          f"{[p.name for p in pred_files]}")

    results: dict[str, dict[str, Any]] = {}
    for pred_file in pred_files:
        with pred_file.open("r", encoding="utf-8") as f:
            pred_data = json.load(f)
        model_name = pred_data["metadata"]["model_name"]
        print(f"Evaluating: {model_name}")
        results[model_name] = evaluate_model(gold_docs, pred_data["documents"])

    # --- Write JSON report ---
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORTS_DIR / "evaluation_report.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"JSON report written to: {json_path}")

    # --- Write Markdown report ---
    md_path = REPORTS_DIR / "evaluation_report.md"
    md_content = build_markdown_report(results)
    with md_path.open("w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Markdown report written to: {md_path}")

    # --- Print summary to console ---
    print("\n=== Summary (Overall micro-averaged F1) ===")
    for model_name, res in results.items():
        print(f"  {model_name}: F1={res['overall']['f1']:.4f}")


if __name__ == "__main__":
    main()
