import os
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from lm_client import LMStudioClient
from models import ChatHistory, KnowledgeBase
from es_search_service import es_search_service


load_dotenv()

app = FastAPI(title="Hannah AI - LM Studio")

# CORS for local UI and tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static UI under /web
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.isdir(static_dir):
    app.mount("/web", StaticFiles(directory=static_dir), name="web")


class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None
    temperature: float = 0.2
    rating: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    history_id: int


def get_lm_client() -> LMStudioClient:
    base_url = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
    api_key = os.getenv("LMSTUDIO_API_KEY", "lm-studio")
    return LMStudioClient(base_url=base_url, api_key=api_key)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    model_name = os.getenv("LMSTUDIO_MODEL", "microsoft/phi-4-mini-reasoning")
    client = get_lm_client()
    answer = client.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": req.message},
        ],
        temperature=req.temperature,
    )

    history = ChatHistory(
        user_id=req.user_id,
        session_id=req.session_id,
        question=req.message,
        answer=answer,
        rating=req.rating,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return ChatResponse(answer=answer, history_id=history.id)


class RateRequest(BaseModel):
    history_id: int
    rating: int


@app.post("/rate")
def rate(req: RateRequest, db: Session = Depends(get_db)):
    item = db.query(ChatHistory).filter(ChatHistory.id == req.history_id).first()
    if not item:
        return {"ok": False, "message": "History not found"}
    item.rating = req.rating
    db.commit()
    return {"ok": True}


# ----------------------------- Knowledge Base ----------------------------- #

class KBCreate(BaseModel):
    title: str
    content: str
    category: str
    created_by: str


class KBUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class KBItem(BaseModel):
    id: int
    title: str
    content: str
    category: str
    created_by: str
    is_active: bool

    class Config:
        from_attributes = True


@app.post("/kb", response_model=KBItem)
def kb_create(payload: KBCreate, db: Session = Depends(get_db)):
    item = KnowledgeBase(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        created_by=payload.created_by,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/kb", response_model=List[KBItem])
def kb_list(category: Optional[str] = None, active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(KnowledgeBase)
    if category:
        q = q.filter(KnowledgeBase.category == category)
    if active_only:
        q = q.filter(KnowledgeBase.is_active.is_(True))
    return q.order_by(KnowledgeBase.id.desc()).all()


@app.get("/kb/{item_id}", response_model=KBItem)
def kb_get(item_id: int, db: Session = Depends(get_db)):
    return db.query(KnowledgeBase).filter(KnowledgeBase.id == item_id).first()


@app.put("/kb/{item_id}", response_model=KBItem)
def kb_update(item_id: int, payload: KBUpdate, db: Session = Depends(get_db)):
    item = db.query(KnowledgeBase).filter(KnowledgeBase.id == item_id).first()
    if not item:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/kb/{item_id}")
def kb_delete(item_id: int, db: Session = Depends(get_db)):
    item = db.query(KnowledgeBase).filter(KnowledgeBase.id == item_id).first()
    if not item:
        return {"ok": False}
    db.delete(item)
    db.commit()
    return {"ok": True}


@app.get("/kb/search", response_model=List[KBItem])
def kb_search(q: str, db: Session = Depends(get_db)):
    pattern = f"%{q}%"
    return (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.is_active.is_(True))
        .filter((KnowledgeBase.title.ilike(pattern)) | (KnowledgeBase.content.ilike(pattern)))
        .order_by(KnowledgeBase.id.desc())
        .all()
    )


# ----------------------------- Elasticsearch Search ----------------------------- #

class ESSearchRequest(BaseModel):
    query: str = "*"
    top_n_per_category: Optional[int] = None
    categories: Optional[List[str]] = None
    save_to_postgres: bool = True
    created_by: str = "api_user"


class ESSearchResponse(BaseModel):
    search_results: Dict[str, List[Dict[str, Any]]]
    saved_to_postgres: int
    saved_items: List[Dict[str, Any]]
    sft_pairs: List[Dict[str, Any]]
    total_results: int
    categories_found: List[str]
    rejected_by_guardrails: int
    query: str
    timestamp: str


@app.post("/es/search", response_model=ESSearchResponse)
def es_search(request: ESSearchRequest):
    """
    Search Elasticsearch, deduplicate results, apply guardrails,
    optionally save to PostgreSQL, and return SFT-ready pairs.
    """
    try:
        result = es_search_service.search_and_save_to_kb(
            query=request.query,
            top_n_per_category=request.top_n_per_category,
            categories=request.categories,
            save_to_postgres=request.save_to_postgres,
            created_by=request.created_by
        )
        return ESSearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/es/categories")
def get_es_categories():
    """Get available categories from Elasticsearch."""
    try:
        categories = es_search_service.get_categories()
        return {"categories": categories, "count": len(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


class SFTExportRequest(BaseModel):
    query: str = "*"
    categories: Optional[List[str]] = None
    top_n_per_category: int = 10
    include_metadata: bool = True


@app.post("/es/export-sft")
def export_sft_pairs(request: SFTExportRequest):
    """
    Export SFT-ready training pairs from Elasticsearch without saving to PostgreSQL.
    Useful for generating training data.
    """
    try:
        result = es_search_service.search_and_save_to_kb(
            query=request.query,
            top_n_per_category=request.top_n_per_category,
            categories=request.categories,
            save_to_postgres=False,  # Don't save to PostgreSQL
            created_by="export"
        )

        sft_pairs = result["sft_pairs"]

        # Remove metadata if not requested
        if not request.include_metadata:
            for pair in sft_pairs:
                pair.pop("metadata", None)

        return {
            "sft_pairs": sft_pairs,
            "total_pairs": len(sft_pairs),
            "categories_found": result["categories_found"],
            "query": request.query,
            "timestamp": result["timestamp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.get("/es/search-simple")
def es_search_simple(
    q: str = Query("*", description="Search query"),
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    top_n: int = Query(10, description="Top N results per category"),
    save: bool = Query(False, description="Save results to PostgreSQL")
):
    """
    Simple GET endpoint for Elasticsearch search with query parameters.
    """
    try:
        category_list = None
        if categories:
            category_list = [cat.strip() for cat in categories.split(",")]

        result = es_search_service.search_and_save_to_kb(
            query=q,
            top_n_per_category=top_n,
            categories=category_list,
            save_to_postgres=save,
            created_by="simple_search"
        )

        return {
            "results": result["search_results"],
            "total_results": result["total_results"],
            "categories_found": result["categories_found"],
            "saved_to_postgres": result["saved_to_postgres"] if save else 0,
            "rejected_by_guardrails": result["rejected_by_guardrails"],
            "query": q
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/es/comprehensive-search")
def comprehensive_es_search(request: ESSearchRequest):
    """
    Comprehensive Elasticsearch search endpoint with all features:
    - Pull top-N ES results per KB category
    - Deduplicate content using content hashes
    - Apply guardrails to filter low-quality content
    - Automatically save new knowledge to PostgreSQL knowledge_base table
    - Return SFT-ready training pairs

    This endpoint demonstrates the complete workflow requested.
    """
    try:
        # Perform comprehensive search with all features
        result = es_search_service.search_and_save_to_kb(
            query=request.query,
            top_n_per_category=request.top_n_per_category,
            categories=request.categories,
            save_to_postgres=request.save_to_postgres,
            created_by=request.created_by
        )

        # Add summary statistics
        summary = {
            "workflow_completed": True,
            "features_applied": [
                "elasticsearch_search",
                "category_grouping",
                "content_deduplication",
                "quality_guardrails",
                "postgresql_auto_save" if request.save_to_postgres else "postgresql_save_skipped",
                "sft_pair_generation"
            ],
            "performance_metrics": {
                "total_found": result["total_results"],
                "quality_filtered": result["rejected_by_guardrails"],
                "saved_to_db": result["saved_to_postgres"],
                "sft_pairs_generated": len(result["sft_pairs"]),
                "categories_processed": len(result["categories_found"])
            }
        }

        return {
            **result,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comprehensive search failed: {str(e)}"
        )


