from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from models import ChatHistory, KnowledgeBase, UserProfile
from llm_service import llm_service
import uuid

app = FastAPI(title="Hannah AI Learning Assistant", version="1.0.0")

# Pydantic models
class ChatRequest(BaseModel):
    user_id: str
    question: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    context_used: Optional[str] = None

class KnowledgeRequest(BaseModel):
    title: str
    content: str
    category: str
    created_by: str

# Simple knowledge retrieval (thay thế Elasticsearch cho demo)
def search_knowledge(query: str, db: Session, limit: int = 3) -> str:
    """
    Tìm kiếm trong knowledge base đơn giản
    """
    knowledge = db.query(KnowledgeBase).filter(
        KnowledgeBase.content.contains(query.lower())
    ).limit(limit).all()
    
    if knowledge:
        context = "\n\n".join([f"- {k.title}: {k.content[:200]}..." for k in knowledge])
        return context
    return ""

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint
    """
    # Tạo session_id nếu chưa có
    session_id = request.session_id or str(uuid.uuid4())
    
    # Tìm context từ knowledge base
    context = search_knowledge(request.question, db)
    
    # Generate response từ LM Studio
    answer = llm_service.generate_response(request.question, context)
    
    # Lưu vào database
    chat_record = ChatHistory(
        user_id=request.user_id,
        session_id=session_id,
        question=request.question,
        answer=answer,
        context_used=context if context else None
    )
    db.add(chat_record)
    db.commit()
    
    return ChatResponse(
        answer=answer,
        session_id=session_id,
        context_used=context if context else None
    )

@app.post("/knowledge")
async def add_knowledge(request: KnowledgeRequest, db: Session = Depends(get_db)):
    """
    Faculty/Admin thêm knowledge
    """
    knowledge = KnowledgeBase(
        title=request.title,
        content=request.content,
        category=request.category,
        created_by=request.created_by
    )
    db.add(knowledge)
    db.commit()
    return {"message": "Knowledge added successfully"}

@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, db: Session = Depends(get_db)):
    """
    Lấy lịch sử chat của user
    """
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == user_id
    ).order_by(ChatHistory.created_at.desc()).limit(10).all()
    
    return [
        {
            "question": h.question,
            "answer": h.answer,
            "created_at": h.created_at,
            "session_id": h.session_id
        }
        for h in history
    ]

@app.get("/")
async def root():
    return {"message": "Hannah AI Learning Assistant is running!"}