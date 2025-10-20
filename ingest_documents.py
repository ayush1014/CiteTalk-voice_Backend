"""
Sample script to ingest documents into the RAG system.
This adds knowledge to the AI agent that it can use to answer questions.
"""
import requests
import json

API_BASE_URL = "http://localhost:8000/api"

def ingest_sample_documents():
    """
    Ingest sample documents about AI and machine learning.
    """
    documents = [
        {
            "text": """
            Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, 
            especially computer systems. These processes include learning (the acquisition of information 
            and rules for using the information), reasoning (using rules to reach approximate or definite 
            conclusions), and self-correction. AI applications include expert systems, natural language 
            processing, speech recognition, and machine vision.
            """,
            "metadata": {"source": "ai_basics", "topic": "artificial_intelligence"}
        },
        {
            "text": """
            Machine Learning (ML) is a subset of artificial intelligence that provides systems the ability 
            to automatically learn and improve from experience without being explicitly programmed. 
            Machine learning focuses on the development of computer programs that can access data and 
            use it to learn for themselves. The primary aim is to allow computers to learn automatically 
            without human intervention or assistance.
            """,
            "metadata": {"source": "ml_basics", "topic": "machine_learning"}
        },
        {
            "text": """
            Large Language Models (LLMs) are a type of artificial intelligence model designed to understand 
            and generate human-like text. These models are trained on vast amounts of text data and can 
            perform various language tasks such as translation, summarization, question answering, and 
            creative writing. Examples include GPT-4, Claude, and PaLM. LLMs have revolutionized natural 
            language processing and are now used in chatbots, content generation, and many other applications.
            """,
            "metadata": {"source": "llm_basics", "topic": "large_language_models"}
        },
        {
            "text": """
            RAG (Retrieval-Augmented Generation) is a technique that combines information retrieval with 
            text generation. It works by first retrieving relevant documents from a knowledge base, then 
            using those documents as context for a language model to generate accurate and informed responses. 
            This approach helps reduce hallucinations and provides more factual, grounded answers by giving 
            the model access to external knowledge.
            """,
            "metadata": {"source": "rag_basics", "topic": "rag"}
        },
        {
            "text": """
            Vector databases store data as high-dimensional vectors, which are mathematical representations 
            of data points. They enable similarity search, where you can find items similar to a query 
            by measuring the distance between vectors. This is particularly useful for AI applications 
            like semantic search, recommendation systems, and RAG systems. pgvector is a popular PostgreSQL 
            extension that adds vector similarity search capabilities.
            """,
            "metadata": {"source": "vector_db_basics", "topic": "vector_databases"}
        }
    ]
    
    # Prepare the request
    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    payload = {
        "texts": texts,
        "metadatas": metadatas
    }
    
    print("🚀 Ingesting documents into the RAG system...")
    print(f"📄 Number of documents: {len(texts)}")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/ingest",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        result = response.json()
        print("✅ Success!")
        print(f"📊 {result['message']}")
        print(f"🆔 Document IDs: {result['document_ids']}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")


def test_query(query: str):
    """
    Test a query against the RAG system.
    """
    payload = {
        "query": query,
        "session_id": "test-session"
    }
    
    print(f"\n💬 Testing query: '{query}'")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        result = response.json()
        print("🤖 AI Response:")
        print(result['response'])
        print()
        print(f"🎯 Intent: {result.get('intent', 'N/A')}")
        print(f"📚 Used Context: {result.get('context_used', False)}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")


if __name__ == "__main__":
    print("=" * 60)
    print("Live 3D AI Agent - Document Ingestion Script")
    print("=" * 60)
    print()
    
    # Ingest documents
    ingest_sample_documents()
    
    # Test some queries
    print("\n" + "=" * 60)
    print("Testing Queries")
    print("=" * 60)
    
    test_queries = [
        "What is artificial intelligence?",
        "Explain RAG to me",
        "What are vector databases used for?",
        "How do large language models work?"
    ]
    
    for query in test_queries:
        test_query(query)
        print()
    
    print("=" * 60)
    print("✅ All done!")
    print("=" * 60)
