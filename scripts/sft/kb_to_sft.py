import json
from database import SessionLocal
from models import KnowledgeBase


def main() -> None:
    session = SessionLocal()
    rows = (
        session.query(KnowledgeBase)
        .filter(KnowledgeBase.is_active.is_(True))
        .all()
    )
    with open("data/kb_sft.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            # Turn KB entry into a simple instruction-answer pair
            item = {
                "messages": [
                    {"role": "user", "content": f"Explain: {r.title}"},
                    {"role": "assistant", "content": r.content},
                ],
                "weight": 0.7,
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print("Wrote data/kb_sft.jsonl")


if __name__ == "__main__":
    main()


