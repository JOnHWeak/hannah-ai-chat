import os
import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from es_client import search_es_by_category, get_es_client
from models import KnowledgeBase
from database import SessionLocal


class ContentGuardrails:
    """Content quality validation and filtering."""

    def __init__(self, min_content_length: int = 50, max_content_length: int = 10000):
        self.min_content_length = min_content_length
        self.max_content_length = max_content_length

        # Patterns for low-quality content
        self.spam_patterns = [
            r'^(.)\1{10,}',  # Repeated characters
            r'^\s*$',        # Empty or whitespace only
            r'^[^a-zA-Z]*$', # No alphabetic characters
        ]

        # Common spam/placeholder words
        self.spam_words = {
            'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur',
            'test', 'testing', 'placeholder', 'example', 'sample',
            'todo', 'fixme', 'xxx', 'yyy', 'zzz'
        }

    def is_valid_content(self, content: str, title: str = "") -> tuple[bool, str]:
        """
        Validate content quality.

        Returns:
            (is_valid, reason) - True if content passes all checks
        """
        if not content or not content.strip():
            return False, "Empty content"

        content_clean = content.strip()

        # Length checks
        if len(content_clean) < self.min_content_length:
            return False, f"Content too short ({len(content_clean)} < {self.min_content_length})"

        if len(content_clean) > self.max_content_length:
            return False, f"Content too long ({len(content_clean)} > {self.max_content_length})"

        # Spam pattern checks
        for pattern in self.spam_patterns:
            if re.search(pattern, content_clean, re.IGNORECASE):
                return False, f"Matches spam pattern: {pattern}"

        # Check for excessive spam words
        words = set(re.findall(r'\b\w+\b', content_clean.lower()))
        spam_word_count = len(words.intersection(self.spam_words))
        if spam_word_count > 3:
            return False, f"Too many spam words ({spam_word_count})"

        # Check content-to-title ratio (avoid very repetitive content)
        if title and len(title.strip()) > 0:
            title_words = set(re.findall(r'\b\w+\b', title.lower()))
            content_words = set(re.findall(r'\b\w+\b', content_clean.lower()))

            if len(content_words) > 0:
                overlap_ratio = len(title_words.intersection(content_words)) / len(content_words)
                if overlap_ratio > 0.8:  # More than 80% overlap
                    return False, "Content too similar to title"

        return True, "Valid content"

    def filter_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter results based on content quality."""
        filtered = []

        for item in results:
            content = item.get("content", "")
            title = item.get("title", "")

            is_valid, reason = self.is_valid_content(content, title)

            if is_valid:
                filtered.append(item)
            else:
                # Add rejection reason to metadata for debugging
                item["rejection_reason"] = reason

        return filtered


class ESSearchService:
    """Service for Elasticsearch search with PostgreSQL integration."""

    def __init__(self):
        self.index_name = os.getenv("KB_INDEX", "kb_software_engineering")
        self.min_content_length = int(os.getenv("MIN_CONTENT_LENGTH", "50"))
        self.max_content_length = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))
        self.default_top_n = int(os.getenv("DEFAULT_TOP_N_PER_CATEGORY", "10"))

        # Initialize guardrails
        self.guardrails = ContentGuardrails(
            min_content_length=self.min_content_length,
            max_content_length=self.max_content_length
        )
    
    def search_and_save_to_kb(
        self,
        query: str = "*",
        top_n_per_category: Optional[int] = None,
        categories: Optional[List[str]] = None,
        save_to_postgres: bool = True,
        created_by: str = "es_search_auto"
    ) -> Dict[str, Any]:
        """
        Search ES, apply guardrails, optionally save to PostgreSQL, and return SFT-ready data.
        
        Args:
            query: Search query
            top_n_per_category: Max results per category (uses default if None)
            categories: Specific categories to search
            save_to_postgres: Whether to save new knowledge to PostgreSQL
            created_by: Who created the knowledge (for PostgreSQL records)
        
        Returns:
            Dict with search results, saved items, and SFT-ready pairs
        """
        if top_n_per_category is None:
            top_n_per_category = self.default_top_n
            
        # Search Elasticsearch with deduplication
        category_results = search_es_by_category(
            query=query,
            index_name=self.index_name,
            top_n_per_category=top_n_per_category,
            min_content_length=self.min_content_length,
            categories=categories
        )

        # Apply enhanced guardrails to filter results
        filtered_results = {}
        rejected_count = 0

        for category, results in category_results.items():
            filtered = self.guardrails.filter_results(results)
            rejected_count += len(results) - len(filtered)
            if filtered:  # Only include categories with valid results
                filtered_results[category] = filtered

        saved_items = []
        sft_pairs = []

        if save_to_postgres:
            saved_items = self._save_to_postgres(filtered_results, created_by)

        # Generate SFT-ready pairs
        sft_pairs = self._generate_sft_pairs(filtered_results)
        
        return {
            "search_results": filtered_results,
            "saved_to_postgres": len(saved_items),
            "saved_items": saved_items,
            "sft_pairs": sft_pairs,
            "total_results": sum(len(results) for results in filtered_results.values()),
            "categories_found": list(filtered_results.keys()),
            "rejected_by_guardrails": rejected_count,
            "query": query,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _save_to_postgres(
        self,
        category_results: Dict[str, List[Dict[str, Any]]],
        created_by: str
    ) -> List[Dict[str, Any]]:
        """Save new knowledge items to PostgreSQL knowledge_base table with enhanced tracking."""
        db = SessionLocal()
        saved_items = []
        skipped_items = []
        error_items = []

        try:
            # Get existing content hashes to avoid duplicates
            existing_hashes = self._get_existing_content_hashes(db)

            for category, results in category_results.items():
                for item in results:
                    content_hash = item.get("content_hash")
                    title = item.get("title", "").strip()
                    content = item.get("content", "").strip()

                    # Skip if already exists in PostgreSQL
                    if content_hash in existing_hashes:
                        skipped_items.append({
                            "title": title,
                            "reason": "duplicate_content_hash",
                            "content_hash": content_hash
                        })
                        continue

                    # Additional validation before saving
                    if not title or not content:
                        skipped_items.append({
                            "title": title or "No title",
                            "reason": "missing_title_or_content",
                            "content_hash": content_hash
                        })
                        continue

                    try:
                        # Create new knowledge base entry
                        kb_item = KnowledgeBase(
                            title=title[:200],  # Respect DB column limit
                            content=content,
                            category=category,
                            created_by=f"{created_by}_es_auto",  # Mark as ES auto-imported
                            is_active=True
                        )

                        db.add(kb_item)
                        db.flush()  # Get the ID without committing

                        saved_items.append({
                            "id": kb_item.id,
                            "title": kb_item.title,
                            "category": category,
                            "content_length": len(kb_item.content),
                            "es_score": item.get("score", 0),
                            "es_id": item.get("es_id"),
                            "content_hash": content_hash,
                            "created_by": kb_item.created_by
                        })

                        # Add to existing hashes to prevent duplicates in same batch
                        existing_hashes.add(content_hash)

                    except Exception as item_error:
                        error_items.append({
                            "title": title,
                            "error": str(item_error),
                            "content_hash": content_hash
                        })
                        continue

            # Commit all successful items
            db.commit()

            # Log summary
            print(f"PostgreSQL save summary: {len(saved_items)} saved, {len(skipped_items)} skipped, {len(error_items)} errors")

        except Exception as e:
            db.rollback()
            print(f"Error saving to PostgreSQL: {e}")
            raise
        finally:
            db.close()

        # Return detailed results
        for item in saved_items:
            item["save_status"] = "success"

        return saved_items
    
    def _get_existing_content_hashes(self, db: Session) -> Set[str]:
        """Get content hashes of existing knowledge base items."""
        from es_client import _generate_content_hash
        
        existing_items = db.query(KnowledgeBase).filter(
            KnowledgeBase.is_active == True
        ).all()
        
        return {_generate_content_hash(item.content) for item in existing_items}
    
    def _generate_sft_pairs(
        self, 
        category_results: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Generate SFT-ready training pairs from search results."""
        sft_pairs = []
        
        for category, results in category_results.items():
            for item in results:
                title = item.get("title", "").strip()
                content = item.get("content", "").strip()
                
                if not title or not content:
                    continue
                
                # Create instruction-response pair
                sft_pair = {
                    "messages": [
                        {
                            "role": "user", 
                            "content": f"Explain: {title}"
                        },
                        {
                            "role": "assistant", 
                            "content": content
                        }
                    ],
                    "weight": 0.7,  # Default weight for ES-sourced content
                    "metadata": {
                        "category": category,
                        "es_score": item.get("score", 0),
                        "es_id": item.get("es_id"),
                        "content_hash": item.get("content_hash"),
                        "source": "elasticsearch"
                    }
                }
                
                sft_pairs.append(sft_pair)
        
        return sft_pairs
    
    def get_categories(self) -> List[str]:
        """Get available categories from Elasticsearch."""
        es = get_es_client()
        
        try:
            # Use aggregation to get unique categories
            search_body = {
                "size": 0,
                "aggs": {
                    "categories": {
                        "terms": {
                            "field": "category",
                            "size": 100
                        }
                    }
                }
            }
            
            response = es.search(index=self.index_name, body=search_body)
            
            categories = []
            if "aggregations" in response and "categories" in response["aggregations"]:
                for bucket in response["aggregations"]["categories"]["buckets"]:
                    categories.append(bucket["key"])
            
            return categories
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []


# Global service instance
es_search_service = ESSearchService()
