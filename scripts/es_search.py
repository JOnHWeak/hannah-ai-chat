import sys
from es_client import get_es_client

INDEX = "kb_software_engineering"


def main() -> None:
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "clean code"
    es = get_es_client()
    res = es.search(index=INDEX, query={"multi_match": {"query": q, "fields": ["title^2", "content"]}}, size=5)
    for hit in res["hits"]["hits"]:
        doc = hit["_source"]
        print(f"- {doc['title']} (score={hit['_score']:.2f})")


if __name__ == "__main__":
    main()


