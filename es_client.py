import os
import hashlib
from typing import Any, Dict, List, Set, Optional
from collections import defaultdict

from dotenv import load_dotenv

try:
    from elasticsearch import Elasticsearch
except Exception:  # pragma: no cover
    Elasticsearch = None  # type: ignore


load_dotenv()


def get_es_client() -> "Elasticsearch":
    if Elasticsearch is None:
        raise RuntimeError("elasticsearch package not installed. Install from requirements-es.txt")
    url = os.getenv("ES_URL", "http://127.0.0.1:9200")
    api_key = os.getenv("ES_API_KEY")
    if api_key:
        return Elasticsearch(url, api_key=api_key)
    username = os.getenv("ES_USERNAME")
    password = os.getenv("ES_PASSWORD")
    if username and password:
        return Elasticsearch(url, basic_auth=(username, password))
    return Elasticsearch(url)


def ensure_index(index_name: str) -> None:
    es = get_es_client()
    if es.indices.exists(index=index_name):
        return
    es.indices.create(
        index=index_name,
        mappings={
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "category": {"type": "keyword"},
                "created_by": {"type": "keyword"},
                "is_active": {"type": "boolean"},
            }
        },
    )


def _generate_content_hash(content: str) -> str:
    """Generate a hash for content deduplication."""
    # Normalize content: strip whitespace, convert to lowercase
    normalized = content.strip().lower()
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


def search_es_by_category(
    query: str = "*",
    index_name: str = "kb_software_engineering",
    top_n_per_category: int = 10,
    min_content_length: int = 50,
    categories: Optional[List[str]] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search Elasticsearch and return top-N results per category with deduplication.

    Args:
        query: Search query (default: "*" for all)
        index_name: ES index name
        top_n_per_category: Maximum results per category
        min_content_length: Minimum content length for guardrails
        categories: Specific categories to search (None for all)

    Returns:
        Dict mapping category names to lists of deduplicated results
    """
    es = get_es_client()

    # Build search query
    if categories:
        # Search specific categories
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query}} if query != "*" else {"match_all": {}},
                        {"terms": {"category": categories}}
                    ],
                    "filter": [
                        {"term": {"is_active": True}}
                    ]
                }
            },
            "size": top_n_per_category * len(categories) * 2,  # Get extra to account for deduplication
            "sort": [{"_score": {"order": "desc"}}]
        }
    else:
        # Search all categories, then group
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query}} if query != "*" else {"match_all": {}}
                    ],
                    "filter": [
                        {"term": {"is_active": True}}
                    ]
                }
            },
            "size": 1000,  # Get a large number to group by category
            "sort": [{"_score": {"order": "desc"}}]
        }

    try:
        response = es.search(index=index_name, body=search_body)
    except Exception as e:
        print(f"Elasticsearch search error: {e}")
        return {}

    # Group results by category and deduplicate
    category_results = defaultdict(list)
    seen_hashes: Set[str] = set()

    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        category = source.get("category", "unknown")
        content = source.get("content", "")

        # Apply guardrails: minimum content length
        if len(content.strip()) < min_content_length:
            continue

        # Generate content hash for deduplication
        content_hash = _generate_content_hash(content)
        if content_hash in seen_hashes:
            continue

        seen_hashes.add(content_hash)

        # Add score and other metadata
        result_item = {
            **source,
            "score": hit["_score"],
            "es_id": hit["_id"],
            "content_hash": content_hash
        }

        category_results[category].append(result_item)

    # Limit results per category
    for category in category_results:
        category_results[category] = category_results[category][:top_n_per_category]

    return dict(category_results)


