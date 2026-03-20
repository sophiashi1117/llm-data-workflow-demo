from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from evaluate import evaluate, write_report
from preprocess import run as preprocess_run
from utils import dump_json, read_jsonl
from workflow import run as workflow_run


def main() -> None:
    cleaned = preprocess_run(
        ROOT / "data" / "raw" / "tickets.jsonl",
        ROOT / "data" / "processed" / "tickets.cleaned.jsonl",
    )
    print(f"[1/3] cleaned_records={len(cleaned)}")

    summary = workflow_run(
        ROOT / "data" / "processed" / "tickets.cleaned.jsonl",
        ROOT / "outputs" / "annotations.jsonl",
        ROOT / "outputs" / "review_queue.jsonl",
        ROOT / "outputs" / "summary.json",
    )
    print(f"[2/3] workflow_summary={summary}")

    metrics = evaluate(
        read_jsonl(ROOT / "outputs" / "annotations.jsonl"),
        read_jsonl(ROOT / "data" / "gold" / "labels.jsonl"),
    )
    dump_json(ROOT / "outputs" / "metrics.json", metrics)
    write_report(metrics, ROOT / "outputs" / "evaluation_report.md")
    print(f"[3/3] metrics={metrics}")


if __name__ == "__main__":
    main()

