from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    session_id = Column(String(100), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    context_used = Column(Text, nullable=True)  # Cho RAG context
    rating = Column(Integer, nullable=True)  # 1-5, do người dùng chấm
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_reviewed = Column(Boolean, default=False)  # Faculty review
    review_notes = Column(Text, nullable=True)

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # Programming, Database, etc.
    created_by = Column(String(100), nullable=False)  # Faculty who added
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    role = Column(String(20), default="student")  # student, faculty, admin
    preferences = Column(Text, nullable=True)  # JSON preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())