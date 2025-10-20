# Live 3D AI Agent - Backend

FastAPI backend for Live 3D AI Avatar with HeyGen Streaming, LangChain RAG, and LangGraph orchestration.

## Features

- **FastAPI** server with async support
- **LangChain** for embeddings and RAG
- **LangGraph** for workflow orchestration
- **pgvector** for vector similarity search
- **HeyGen API** integration for 3D avatar
- **GPT-4o-mini** for conversational AI

## Prerequisites

- Python 3.10+
- PostgreSQL with pgvector extension
- OpenAI API key
- HeyGen API key

## Setup

### 1. Install Dependencies

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Edit the `.env` file with your credentials:

```env
OPENAI_API_KEY=your_openai_api_key_here
HEYGEN_API_KEY=your_heygen_api_key_here
DATABASE_URL=

### 3. Run the Server

**Option 1: Using the run script (Recommended)**
```bash
./run.sh
```

**Option 2: Using uvicorn directly**
```bash
source venv/bin/activate
uvicorn main:app --reload
```

**Option 3: Using Python**
```bash
source venv/bin/activate
python main.py
```

The server will start at `http://localhost:8000`

**Important:** Always use `uvicorn main:app --reload` (NOT `uvicorn app.main:app`)

## API Endpoints

### Chat
- **POST** `/api/chat` - Send a query to the AI agent
  ```json
  {
    "query": "What is AI?",
    "session_id": "unique-session-id"
  }
  ```

### Document Ingestion
- **POST** `/api/ingest` - Ingest documents for RAG
  ```json
  {
    "texts": ["Document content here..."],
    "metadatas": [{"source": "file.txt"}]
  }
  ```

### HeyGen Video
- **GET** `/api/video/{video_id}` - Get video status
- **GET** `/api/video/default` - Get default video
- **POST** `/api/streaming/token` - Get WebRTC streaming token

### Conversation History
- **GET** `/api/history/{session_id}` - Get conversation history
- **POST** `/api/session/new` - Create new session

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼──────────────────────────┐
│      FastAPI Routes             │
├─────────────────────────────────┤
│  ┌──────────────────────────┐  │
│  │   LangGraph Service      │  │
│  │  ┌────────────────────┐  │  │
│  │  │  Intent Node       │  │  │
│  │  │  RAG Retrieve      │  │  │
│  │  │  Generate Response │  │  │
│  │  └────────────────────┘  │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │   RAG Service            │  │
│  │  - LangChain Embeddings  │  │
│  │  - Vector Search         │  │
│  │  - Response Generation   │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │   HeyGen Service         │  │
│  │  - Video API             │  │
│  │  - Streaming Token       │  │
│  └──────────────────────────┘  │
└─────────────┬───────────────────┘
              │
   ┌──────────▼──────────┐
   │  PostgreSQL +       │
   │  pgvector           │
   └─────────────────────┘
```

## Development

### Run with Auto-reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello!", "session_id": "test-123"}'
```

## Database Schema

### documents
- Stores document chunks with embeddings
- Vector similarity search using pgvector

### conversations
- Stores chat history
- Links to session IDs

### heygen_videos
- Caches HeyGen video metadata
- Tracks video status and URLs

## License

MIT
