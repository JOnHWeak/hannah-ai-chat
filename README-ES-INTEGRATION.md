# Elasticsearch Integration with PostgreSQL Auto-Save

This document describes the new Elasticsearch integration features that provide comprehensive search, deduplication, quality filtering, and automatic PostgreSQL knowledge base storage.

## Features Implemented

### 1. 🔍 **Top-N ES Results per Category with Deduplication**
- Search Elasticsearch and group results by knowledge base category
- Configurable top-N results per category (default: 10)
- Content deduplication using MD5 hashes of normalized content
- Prevents duplicate content from being processed

### 2. 🚀 **FastAPI Endpoints for ES Search with SFT-Ready Pairs**
- `/es/search` - Comprehensive search with all features
- `/es/search-simple` - Simple GET endpoint with query parameters  
- `/es/export-sft` - Export SFT training pairs without saving to PostgreSQL
- `/es/comprehensive-search` - Full workflow demonstration
- `/es/categories` - Get available categories from Elasticsearch

### 3. 🛡️ **Content Quality Guardrails**
- Minimum content length validation (default: 50 characters)
- Maximum content length validation (default: 10,000 characters)
- Spam pattern detection (repeated characters, empty content, etc.)
- Spam word filtering (lorem ipsum, placeholder text, etc.)
- Content-to-title similarity checks to avoid repetitive content

### 4. 💾 **PostgreSQL Knowledge Base Auto-Save**
- Automatically save new knowledge from ES searches to `knowledge_base` table
- Duplicate prevention using content hash comparison
- Enhanced error handling and batch processing
- Detailed save statistics and logging
- Configurable creator attribution

## API Endpoints

### Comprehensive Search
```http
POST /es/comprehensive-search
Content-Type: application/json

{
  "query": "clean code",
  "top_n_per_category": 10,
  "categories": ["programming", "software-engineering"],
  "save_to_postgres": true,
  "created_by": "api_user"
}
```

### Simple Search
```http
GET /es/search-simple?q=python&categories=programming,database&top_n=5&save=true
```

### Export SFT Pairs
```http
POST /es/export-sft
Content-Type: application/json

{
  "query": "database design",
  "categories": ["database"],
  "top_n_per_category": 5,
  "include_metadata": true
}
```

### Get Categories
```http
GET /es/categories
```

## Response Format

### Comprehensive Search Response
```json
{
  "search_results": {
    "programming": [
      {
        "title": "Clean Code Principles",
        "content": "Clean code is...",
        "category": "programming",
        "score": 1.5,
        "es_id": "doc123",
        "content_hash": "abc123..."
      }
    ]
  },
  "saved_to_postgres": 5,
  "saved_items": [
    {
      "id": 123,
      "title": "Clean Code Principles",
      "category": "programming",
      "content_length": 500,
      "es_score": 1.5,
      "save_status": "success"
    }
  ],
  "sft_pairs": [
    {
      "messages": [
        {"role": "user", "content": "Explain: Clean Code Principles"},
        {"role": "assistant", "content": "Clean code is..."}
      ],
      "weight": 0.7,
      "metadata": {
        "category": "programming",
        "es_score": 1.5,
        "source": "elasticsearch"
      }
    }
  ],
  "total_results": 15,
  "categories_found": ["programming", "database"],
  "rejected_by_guardrails": 3,
  "query": "clean code",
  "timestamp": "2025-01-10T12:00:00Z",
  "summary": {
    "workflow_completed": true,
    "features_applied": [
      "elasticsearch_search",
      "category_grouping",
      "content_deduplication", 
      "quality_guardrails",
      "postgresql_auto_save",
      "sft_pair_generation"
    ],
    "performance_metrics": {
      "total_found": 15,
      "quality_filtered": 3,
      "saved_to_db": 5,
      "sft_pairs_generated": 12,
      "categories_processed": 2
    }
  }
}
```

## Configuration

Set these environment variables to configure the integration:

```bash
# Elasticsearch Configuration
ES_URL=http://localhost:9200
ES_USERNAME=elastic
ES_PASSWORD=password
ES_API_KEY=your_api_key

# Knowledge Base Configuration  
KB_INDEX=kb_software_engineering
MIN_CONTENT_LENGTH=50
MAX_CONTENT_LENGTH=10000
DEFAULT_TOP_N_PER_CATEGORY=10

# Database Configuration
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/hannah_ai_db
```

## Installation

1. Install Elasticsearch dependencies:
```bash
pip install -r requirements-es.txt
```

2. Ensure Elasticsearch is running and indexed:
```bash
python scripts/ingest/index_kb_to_es.py
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

## Testing

Run the comprehensive test suite:
```bash
python test_es_integration.py
```

This will test all endpoints and demonstrate the complete workflow.

## Workflow Summary

1. **Search**: Query Elasticsearch with configurable parameters
2. **Group**: Organize results by knowledge base category  
3. **Deduplicate**: Remove duplicate content using content hashes
4. **Filter**: Apply quality guardrails to remove low-quality content
5. **Save**: Automatically save new knowledge to PostgreSQL (optional)
6. **Generate**: Create SFT-ready training pairs for model fine-tuning (e.g. `python scripts/sft/es_to_sft.py` or `python scripts/sft/kb_to_sft.py`)

## Benefits

- **Comprehensive**: All requested features in a single integrated solution
- **Quality-Focused**: Multiple layers of content validation and filtering
- **Efficient**: Deduplication prevents processing the same content multiple times
- **Flexible**: Configurable parameters for different use cases
- **Production-Ready**: Error handling, logging, and detailed response metadata
