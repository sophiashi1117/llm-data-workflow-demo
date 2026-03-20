from __future__ import annotations

from pathlib import Path

from utils import dump_json, read_jsonl


def evaluate(pred_items: list[dict], gold_items: list[dict]) -> dict:
    gold_by_id = {item["id"]: item for item in gold_items}

    total = 0
    intent_correct = 0
    severity_correct = 0
    review_correct = 0
    exact_match = 0
    errors = []

    for pred in pred_items:
        gold = gold_by_id.get(pred["id"])
        if not gold:
            continue

        total += 1
        ann = pred["annotation"]

        intent_hit = ann.get("intent") == gold["intent"]
        severity_hit = ann.get("severity") == gold["severity"]
        review_hit = ann.get("needs_human_review") == gold["needs_human_review"]

        intent_correct += int(intent_hit)
        severity_correct += int(severity_hit)
        review_correct += int(review_hit)
        exact_match += int(intent_hit and severity_hit and review_hit)

        if not (intent_hit and severity_hit and review_hit):
            errors.append(
                {
                    "id": pred["id"],
                    "pred": ann,
                    "gold": gold,
                }
            )

    return {
        "total": total,
        "intent_accuracy": round(intent_correct / total, 4) if total else 0,
        "severity_accuracy": round(severity_correct / total, 4) if total else 0,
        "review_flag_accuracy": round(review_correct / total, 4) if total else 0,
        "exact_match": round(exact_match / total, 4) if total else 0,
        "errors": errors,
    }


def write_report(metrics: dict, report_path: Path) -> None:
    lines = [
        "# Evaluation Report",
        "",
        f"- Total samples: {metrics['total']}",
        f"- Intent accuracy: {metrics['intent_accuracy']}",
        f"- Severity accuracy: {metrics['severity_accuracy']}",
        f"- Human review flag accuracy: {metrics['review_flag_accuracy']}",
        f"- Exact match: {metrics['exact_match']}",
        "",
        "## Error Samples",
    ]

    if not metrics["errors"]:
        lines.append("- No mismatches found.")
    else:
        for err in metrics["errors"]:
            lines.append(
                f"- {err['id']}: pred={err['pred']} | gold={err['gold']}"
            )

    report_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    metrics = evaluate(
        read_jsonl(root / "outputs" / "annotations.jsonl"),
        read_jsonl(root / "data" / "gold" / "labels.jsonl"),
    )
    dump_json(root / "outputs" / "metrics.json", metrics)
    write_report(metrics, root / "outputs" / "evaluation_report.md")
    print(metrics)

