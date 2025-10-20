"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class QueryRequest(BaseModel):
    """Request schema for chat queries."""
    query: str = Field(..., description="User query text")
    session_id: str = Field(..., description="Conversation session ID")


class QueryResponse(BaseModel):
    """Response schema for chat queries."""
    response: str
    intent: Optional[str] = None
    context_used: bool = False
    session_id: str


class DocumentIngestRequest(BaseModel):
    """Request schema for document ingestion."""
    texts: List[str] = Field(..., description="List of document texts")
    metadatas: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class DocumentIngestResponse(BaseModel):
    """Response schema for document ingestion."""
    success: bool
    document_ids: List[int]
    message: str


class VideoStatusResponse(BaseModel):
    """Response schema for video status."""
    video_id: str
    status: str
    video_url: Optional[str] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class StreamingTokenResponse(BaseModel):
    """Response schema for streaming token."""
    success: bool
    token: Optional[str] = None
    session_id: Optional[str] = None
    sdp: Optional[Dict[str, Any]] = None
    ice_servers: Optional[List[Dict[str, Any]]] = None
    ice_servers2: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    error: Optional[str] = None


class ConversationHistoryResponse(BaseModel):
    """Response schema for conversation history."""
    session_id: str
    conversations: List[Dict[str, Any]]
    count: int
