"""
RAG service using LangChain and pgvector.
"""
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangChainDocument
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database.models import Document


class RAGService:
    """
    Service for RAG operations with pgvector.
    """
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key
        )
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            temperature=0.7
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
    
    async def ingest_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        db: AsyncSession
    ) -> List[int]:
        """
        Ingest documents into the database with embeddings.
        
        Args:
            texts: List of document texts
            metadatas: List of metadata dictionaries
            db: Database session
            
        Returns:
            List of document IDs
        """
        # Split texts into chunks
        documents = []
        for text, metadata in zip(texts, metadatas):
            chunks = self.text_splitter.split_text(text)
            for chunk in chunks:
                documents.append(
                    LangChainDocument(page_content=chunk, metadata=metadata)
                )
        
        # Generate embeddings
        texts_to_embed = [doc.page_content for doc in documents]
        embeddings = await self.embeddings.aembed_documents(texts_to_embed)
        
        # Store in database
        doc_ids = []
        for doc, embedding in zip(documents, embeddings):
            db_doc = Document(
                content=doc.page_content,
                doc_metadata=doc.metadata,  # Updated field name
                embedding=embedding
            )
            db.add(db_doc)
            await db.flush()
            doc_ids.append(db_doc.id)
        
        await db.commit()
        return doc_ids
    
    async def retrieve_relevant_docs(
        self,
        query: str,
        db: AsyncSession,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents using vector similarity search.
        
        Args:
            query: Search query
            db: Database session
            top_k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if top_k is None:
            top_k = settings.retrieval_top_k
        
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Vector similarity search using pgvector
        # Using cosine distance (1 - cosine similarity)
        query_text = text("""
            SELECT id, content, metadata, 
                   1 - (embedding <=> :query_embedding) as similarity
            FROM documents
            ORDER BY embedding <=> :query_embedding
            LIMIT :top_k
        """)
        
        result = await db.execute(
            query_text,
            {
                "query_embedding": str(query_embedding),
                "top_k": top_k
            }
        )
        
        docs = []
        for row in result:
            docs.append({
                "id": row[0],
                "content": row[1],
                "metadata": row[2],
                "similarity": float(row[3])
            })
        
        return docs
    
    async def generate_response(
        self,
        query: str,
        context_docs: List[Dict[str, Any]]
    ) -> str:
        """
        Generate response using LLM with retrieved context.
        
        Args:
            query: User query
            context_docs: Retrieved context documents
            
        Returns:
            Generated response
        """
        # Build context from retrieved documents
        context = "\n\n".join([doc["content"] for doc in context_docs])
        
        # Create prompt
        prompt = f"""You are a helpful AI assistant. Answer the user's question based on the provided context.
If the context doesn't contain relevant information, use your general knowledge but mention that.

Context:
{context}

User Question: {query}

Answer:"""
        
        # Generate response
        response = await self.llm.ainvoke(prompt)
        return response.content


# Global RAG service instance
rag_service = RAGService()
