from __future__ import annotations

from pathlib import Path

from client import LLMClient, mock_label, mock_review
from prompts import SYSTEM_PROMPT, build_label_prompt, build_review_prompt
from utils import dump_json, read_jsonl, write_jsonl


def route_prompt_version(record: dict) -> str:
    text = record["text"]
    if any(word in text for word in ["退款", "扣费", "支付", "隐私", "泄露"]):
        return "v2-risk-aware"
    if len(text) > 60:
        return "v2-long-context"
    return "v1-base"


def annotate_record(client: LLMClient, record: dict) -> dict:
    prompt_version = route_prompt_version(record)
    prompt = build_label_prompt(record["text"], prompt_version)

    if client.use_remote:
        annotation = client.chat_json(SYSTEM_PROMPT, prompt)
    else:
        annotation = mock_label(record["text"])

    return {
        "id": record["id"],
        "prompt_version": prompt_version,
        "annotation": annotation,
        "raw_text": record["text"],
    }


def review_record(client: LLMClient, item: dict) -> dict:
    prompt = build_review_prompt(item["raw_text"], item["annotation"], item["prompt_version"])

    if client.use_remote:
        review = client.chat_json(SYSTEM_PROMPT, prompt)
    else:
        review = mock_review(item["raw_text"], item["annotation"])

    return {
        **item,
        "review": review,
    }


def run(input_path: Path, annotations_path: Path, review_queue_path: Path, summary_path: Path) -> dict:
    client = LLMClient()
    records = read_jsonl(input_path)

    reviewed_items = []
    review_queue = []

    for record in records:
        annotated = annotate_record(client, record)
        reviewed = review_record(client, annotated)
        reviewed_items.append(reviewed)

        if reviewed["annotation"].get("needs_human_review") or not reviewed["review"].get("pass_review", False):
            review_queue.append(reviewed)

    write_jsonl(annotations_path, reviewed_items)
    write_jsonl(review_queue_path, review_queue)

    summary = {
        "total_records": len(records),
        "remote_model_enabled": client.use_remote,
        "prompt_versions": _count_prompt_versions(reviewed_items),
        "review_queue_size": len(review_queue),
        "review_queue_ratio": round(len(review_queue) / len(records), 4) if records else 0,
    }
    dump_json(summary_path, summary)
    return summary


def _count_prompt_versions(items: list[dict]) -> dict:
    counts = {}
    for item in items:
        version = item["prompt_version"]
        counts[version] = counts.get(version, 0) + 1
    return counts


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = run(
        root / "data" / "processed" / "tickets.cleaned.jsonl",
        root / "outputs" / "annotations.jsonl",
        root / "outputs" / "review_queue.jsonl",
        root / "outputs" / "summary.json",
    )
    print(result)

