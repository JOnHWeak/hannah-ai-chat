import json
import os
from typing import List

from es_client import get_es_client


INDEX = os.getenv("KB_INDEX", "kb_software_engineering")
QUERY = os.getenv("KB_QUERY", "*")
SIZE = int(os.getenv("KB_SIZE", "500"))
OUT = os.getenv("KB_SFT_OUT", "data/kb_es_sft.jsonl")


def search_all() -> List[dict]:
    es = get_es_client()
    results = []
    body = {"query": {"query_string": {"query": QUERY}}}
    resp = es.search(index=INDEX, body=body, size=SIZE)
    for hit in resp["hits"]["hits"]:
        results.append(hit["_source"])
    return results


def to_sft(entries: List[dict]) -> None:
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for e in entries:
            item = {
                "messages": [
                    {"role": "user", "content": f"Explain: {e.get('title','')}"},
                    {"role": "assistant", "content": e.get("content", "")},
                ],
                "weight": 0.6,
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT}")


def main() -> None:
    entries = search_all()
    to_sft(entries)


if __name__ == "__main__":
    main()


