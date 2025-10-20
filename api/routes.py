"""
API routes for the Live 3D AI Agent.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from database import get_db, Conversation
from api.schemas import (
    QueryRequest,
    QueryResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
    ConversationHistoryResponse
)
from services import rag_service, langgraph_service
from config import settings

router = APIRouter()


@router.post("/chat", response_model=QueryResponse)
async def chat(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Chat endpoint using LangGraph orchestration.
    
    Args:
        request: Query request with user message and session ID
        db: Database session
        
    Returns:
        AI response with metadata
    """
    try:
        # Run LangGraph workflow
        result = await langgraph_service.run(
            query=request.query,
            session_id=request.session_id,
            db=db
        )
        
        # Save conversation to database
        conversation = Conversation(
            session_id=request.session_id,
            user_message=request.query,
            assistant_message=result["response"],
            intent=result.get("intent"),
            retrieval_context={
                "docs": result.get("context_docs", [])
            }
        )
        db.add(conversation)
        await db.commit()
        
        return QueryResponse(
            response=result["response"],
            intent=result.get("intent"),
            context_used=len(result.get("context_docs", [])) > 0,
            session_id=request.session_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_documents(
    request: DocumentIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest documents into the RAG system.
    
    Args:
        request: Document ingestion request
        db: Database session
        
    Returns:
        Success status and document IDs
    """
    try:
        # Ensure metadatas list matches texts length
        metadatas = request.metadatas
        if not metadatas:
            metadatas = [{} for _ in request.texts]
        elif len(metadatas) < len(request.texts):
            metadatas.extend([{} for _ in range(len(request.texts) - len(metadatas))])
        
        # Ingest documents
        doc_ids = await rag_service.ingest_documents(
            texts=request.texts,
            metadatas=metadatas,
            db=db
        )
        
        return DocumentIngestResponse(
            success=True,
            document_ids=doc_ids,
            message=f"Successfully ingested {len(doc_ids)} documents"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting documents: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """
    Get conversation history for a session.
    
    Args:
        session_id: Conversation session ID
        db: Database session
        limit: Maximum number of conversations to return
        
    Returns:
        Conversation history
    """
    try:
        from sqlalchemy import select, desc
        
        result = await db.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .order_by(desc(Conversation.created_at))
            .limit(limit)
        )
        
        conversations = result.scalars().all()
        
        conv_list = [
            {
                "id": conv.id,
                "user_message": conv.user_message,
                "assistant_message": conv.assistant_message,
                "intent": conv.intent,
                "created_at": conv.created_at.isoformat() if conv.created_at else None
            }
            for conv in reversed(conversations)
        ]
        
        return ConversationHistoryResponse(
            session_id=session_id,
            conversations=conv_list,
            count=len(conv_list)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving history: {str(e)}"
        )


@router.post("/session/new")
async def create_new_session():
    """
    Create a new conversation session.
    
    Returns:
        New session ID
    """
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


# ===== Simli + LiveKit Routes =====

@router.post("/simli/session")
async def create_simli_session(request: dict = None):
    """
    Create a new Simli + LiveKit avatar session.
    
    Args:
        request: Can contain optional room_name and instructions
        
    Returns:
        Session info with room_url and access_token
    """
    try:
        from services.simli_service import simli_service
        
        print(f"\n📥 /simli/session called with request: {request}")
        print(f"📥 Request type: {type(request)}\n")
        
        # Handle None request
        if request is None:
            request = {}
        
        # Generate room name if not provided or is None
        room_name = request.get("room_name") or f"room-{uuid.uuid4()}"
        instructions = request.get("instructions") or "You are a helpful AI assistant. Talk to me!"
        
        print(f"📝 Generated room_name: {room_name}")
        print(f"📝 Instructions: {instructions}\n")
        
        result = await simli_service.create_avatar_session(room_name, instructions)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to create session")
            )
        
        # Trigger agent to join the room
        print(f"🤖 Triggering agent dispatch for room: {room_name}")
        await simli_service.trigger_agent_for_room(room_name, instructions)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating Simli session: {str(e)}"
        )


@router.post("/simli/speak")
async def simli_speak(request: dict):
    """
    Send text for the Simli avatar to speak.
    
    Args:
        request: Contains session_id and text
        
    Returns:
        Success status
    """
    try:
        from services.simli_service import simli_service
        
        session_id = request.get("session_id")
        text = request.get("text")
        
        if not session_id or not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id and text are required"
            )
        
        result = await simli_service.send_message_to_avatar(session_id, text)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to send message")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in Simli speak: {str(e)}"
        )


@router.post("/simli/stop")
async def stop_simli_session(request: dict):
    """
    Stop a Simli avatar session.
    
    Args:
        request: Contains session_id
        
    Returns:
        Success status
    """
    try:
        from services.simli_service import simli_service
        
        session_id = request.get("session_id")
        
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id is required"
            )
        
        result = await simli_service.stop_session(session_id)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to stop session")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping Simli session: {str(e)}"
        )
