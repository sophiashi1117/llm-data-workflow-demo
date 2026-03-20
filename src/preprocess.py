from __future__ import annotations

import re
from pathlib import Path

from utils import read_jsonl, write_jsonl


def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("，", ", ").replace("。", ". ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def preprocess_records(records: list[dict]) -> list[dict]:
    seen = set()
    cleaned = []

    for record in records:
        text = normalize_text(record["text"])
        if len(text) < 12:
            continue

        # Deduplicate by normalized content so cross-channel duplicates only keep one copy.
        dedupe_key = text.lower()
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        cleaned.append(
            {
                "id": record["id"],
                "source": record.get("source", "unknown"),
                "text": text,
                "meta": {
                    "created_at": record.get("created_at", ""),
                    "language": record.get("language", "zh"),
                },
            }
        )
    return cleaned


def run(input_path: Path, output_path: Path) -> list[dict]:
    raw_records = read_jsonl(input_path)
    cleaned = preprocess_records(raw_records)
    write_jsonl(output_path, cleaned)
    return cleaned


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    records = run(
        root / "data" / "raw" / "tickets.jsonl",
        root / "data" / "processed" / "tickets.cleaned.jsonl",
    )
    print(f"preprocessed_records={len(records)}")
