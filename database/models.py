"""
Database models for the Live 3D AI Agent.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from database.db import Base


class Document(Base):
    """
    Model for storing documents and their embeddings.
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    doc_metadata = Column(JSON, default={})  # Renamed to avoid conflict with SQLAlchemy's metadata
    embedding = Column(Vector(1536))  # OpenAI embedding dimension
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Conversation(Base):
    """
    Model for storing conversation history.
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    user_message = Column(Text, nullable=False)
    assistant_message = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    retrieval_context = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HeyGenVideo(Base):
    """
    Model for storing HeyGen video metadata.
    """
    __tablename__ = "heygen_videos"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, unique=True, index=True, nullable=False)
    video_url = Column(String, nullable=True)
    status = Column(String, nullable=False)  # pending, processing, completed, failed
    duration = Column(Float, nullable=True)
    query_context = Column(Text, nullable=True)
    video_metadata = Column(JSON, default={})  # Renamed to avoid conflict with SQLAlchemy's metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
