from typing import Iterable

from database import SessionLocal
from models import KnowledgeBase
from es_client import get_es_client, ensure_index


INDEX = "kb_software_engineering"


def fetch_rows(batch_size: int = 500) -> Iterable[KnowledgeBase]:
    session = SessionLocal()
    try:
        offset = 0
        while True:
            rows = (
                session.query(KnowledgeBase)
                .filter(KnowledgeBase.is_active.is_(True))
                .order_by(KnowledgeBase.id)
                .offset(offset)
                .limit(batch_size)
                .all()
            )
            if not rows:
                break
            for r in rows:
                yield r
            offset += len(rows)
    finally:
        session.close()


def main() -> None:
    es = get_es_client()
    ensure_index(INDEX)
    operations = []
    for row in fetch_rows():
        operations.append({
            "index": {"_index": INDEX, "_id": row.id}
        })
        operations.append({
            "title": row.title,
            "content": row.content,
            "category": row.category,
            "created_by": row.created_by,
            "is_active": row.is_active,
        })
        if len(operations) >= 1000:
            es.bulk(operations=operations)
            operations = []
    if operations:
        es.bulk(operations=operations)
    print("Indexed KB into Elasticsearch")


if __name__ == "__main__":
    main()


