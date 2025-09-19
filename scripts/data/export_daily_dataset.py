import os
import json
import datetime as dt

from database import SessionLocal
from models import ChatHistory


def main() -> None:
    since = dt.datetime.utcnow() - dt.timedelta(days=1)

    session = SessionLocal()
    try:
        rows = (
            session.query(ChatHistory)
            .filter(ChatHistory.created_at >= since)
            .filter(ChatHistory.rating != None)  # noqa: E711
            .filter(ChatHistory.rating >= 4)
            .all()
        )
    finally:
        session.close()

    os.makedirs("data/daily", exist_ok=True)
    out_path = f"data/daily/{dt.date.today().isoformat()}.jsonl"

    with open(out_path, "w", encoding="utf-8") as f:
        for r in rows:
            item = {
                "messages": [
                    {"role": "user", "content": r.question},
                    {"role": "assistant", "content": r.answer},
                ],
                "weight": min(1.0, 0.2 * int(r.rating or 0)),
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows)} rows -> {out_path}")


if __name__ == "__main__":
    main()



