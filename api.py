"""
api.py - FastAPI Backend for Roamora Travels RAG Chatbot
Exposes REST endpoints to query the knowledge base and return grounded answers.
"""

import os
import logging
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import our RAG functions
from rag import load_company_documents, build_vector_store, query_rag_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("roamora-rag-api")

# Load environment variables
load_dotenv()

# Global state to hold pre-computed vector store
rag_state: Dict[str, Any] = {
    "vector_store": None,
    "api_key": None,
    "provider": "gemini",
    "is_ready": False
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event: Loads store files and builds FAISS index once at startup.
    This guarantees zero re-indexing latency during user chat queries.
    """
    logger.info("Initializing Roamora Travels RAG Knowledge Base...")
    
    # 1. Check for API key (Prioritizes GEMINI, falls back to OPENAI)
    gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if gemini_key:
        provider = "gemini"
        api_key = gemini_key
    elif openai_key:
        provider = "openai"
        api_key = openai_key
    else:
        logger.warning("No GOOGLE_API_KEY or GEMINI_API_KEY or OPENAI_API_KEY found in .env. RAG queries will require key in request or .env.")
        provider = "gemini"
        api_key = None

    rag_state["provider"] = provider
    rag_state["api_key"] = api_key

    # 2. Build index if API key is present
    if api_key:
        try:
            txt_path = "data/company_info.txt"
            xlsx_path = "data/products.xlsx"
            docs = load_company_documents(txt_path=txt_path, xlsx_path=xlsx_path)
            
            if docs:
                vector_store, chunks = build_vector_store(
                    documents=docs,
                    api_key=api_key,
                    provider=provider,
                    chunk_size=500,
                    chunk_overlap=50
                )
                rag_state["vector_store"] = vector_store
                rag_state["is_ready"] = True
                logger.info(f"RAG Knowledge Base initialized with {len(docs)} documents and {len(chunks)} chunks.")
            else:
                logger.error("No documents found in data/ directory to build index.")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}", exc_info=True)
            
    yield
    
    logger.info("Shutting down Roamora Travels RAG API...")


# Create FastAPI application
app = FastAPI(
    title="Roamora Travels RAG API",
    description="REST backend providing grounded travel advisory and tour catalog answers.",
    version="1.0.1",
    lifespan=lifespan
)

# Enable CORS for all frontend origins (Lovable, Vite localhost, custom domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# PYDANTIC DATA MODELS
# ==========================================
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Traveler question or prompt.")
    k: Optional[int] = Field(3, ge=1, le=10, description="Number of top chunks to retrieve.")
    api_key: Optional[str] = Field(None, description="Optional override for API key.")


class SourceChunk(BaseModel):
    file_name: str
    source_type: str
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]


# ==========================================
# API ENDPOINTS
# ==========================================
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "service": "Roamora Travels AI Advisor API",
        "ready": rag_state["is_ready"],
        "provider": rag_state["provider"]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy" if rag_state["is_ready"] else "not_ready",
        "index_loaded": rag_state["vector_store"] is not None
    }


@app.post("/reload", tags=["Admin"])
async def reload_index():
    """Rebuilds the FAISS vector index from updated files in data/ directory."""
    api_key = rag_state.get("api_key")
    if not api_key:
        raise HTTPException(status_code=400, detail="API key not configured.")
    try:
        docs = load_company_documents("data/company_info.txt", "data/products.xlsx")
        vector_store, chunks = build_vector_store(
            documents=docs,
            api_key=api_key,
            provider=rag_state["provider"]
        )
        rag_state["vector_store"] = vector_store
        rag_state["is_ready"] = True
        return {"status": "reloaded", "documents": len(docs), "chunks": len(chunks)}
    except Exception as e:
        logger.error(f"Failed to reload index: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Receives traveler query, retrieves relevant knowledge base chunks,
    and returns strictly grounded answers with source citations.
    """
    api_key = request.api_key or rag_state.get("api_key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not configured on server and none provided in request."
        )

    # If vector store wasn't built at startup, build it on demand
    vector_store = rag_state.get("vector_store")
    if not vector_store:
        try:
            docs = load_company_documents("data/company_info.txt", "data/products.xlsx")
            vector_store, _ = build_vector_store(
                documents=docs,
                api_key=api_key,
                provider=rag_state["provider"]
            )
            rag_state["vector_store"] = vector_store
            rag_state["is_ready"] = True
        except Exception as e:
            logger.error(f"Error building vector store on demand: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to build vector index: {str(e)}"
            )

    try:
        result = query_rag_pipeline(
            question=request.query,
            vector_store=vector_store,
            api_key=api_key,
            provider=rag_state["provider"],
            k=request.k or 3
        )

        sources = []
        for doc in result.get("retrieved_chunks", []):
            sources.append(SourceChunk(
                file_name=doc.metadata.get("file_name", "Roamora Knowledge Base"),
                source_type=doc.metadata.get("source_type", "Store Document"),
                content=doc.page_content.strip()
            ))

        return ChatResponse(
            answer=result.get("answer", "I don't know."),
            sources=sources
        )

    except Exception as e:
        logger.error(f"Error querying RAG pipeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating answer: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
