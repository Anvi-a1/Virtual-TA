import os
import json
import numpy as np
import faiss
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from google import genai  # ✅ Correct import for google-genai package
from google.genai import types  # Import types for configuration
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
FAISS_INDEX_PATH = "model/virtual-ta.faiss"
METADATA_PATH = "model/metadata.json"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SIMILARITY_THRESHOLD = 0
TOP_K_RESULTS = 5

# Initialize Gemini client
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not set in environment")
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = genai.Client(api_key=GEMINI_API_KEY)

# Load FAISS index and metadata
try:
    logger.info(f"Loading FAISS index from {FAISS_INDEX_PATH}")
    index = faiss.read_index(FAISS_INDEX_PATH)
    
    logger.info(f"Loading metadata from {METADATA_PATH}")
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    logger.info(f"Loaded {index.ntotal} vectors and {len(metadata)} metadata entries")
except Exception as e:
    logger.error(f"Failed to load FAISS index or metadata: {e}")
    raise

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

class LinkInfo(BaseModel):
    url: str
    text: str

class QueryResponse(BaseModel):
    answer: str
    links: List[LinkInfo]

# Initialize FastAPI app
app = FastAPI(
    title="VirtualTA Query API",
    description="RAG API using Gemini embeddings and FAISS"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_embedding(text: str) -> np.ndarray:
    """Get embedding from Gemini API"""
    try:
        logger.info(f"Getting embedding for text (length: {len(text)})")
        
        # ✅ Updated for google-genai package
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        
        embedding = np.array(result.embeddings[0].values, dtype=np.float32)
        # Normalize for cosine similarity
        normalized = embedding / np.linalg.norm(embedding)
        return normalized
    except Exception as e:
        logger.error(f"Error getting embedding: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")


def search_similar(query_embedding: np.ndarray, top_k: int = TOP_K_RESULTS) -> List[dict]:
    """Search FAISS index for similar vectors"""
    try:
        logger.info(f"Searching FAISS index for top {top_k} results")
        
        # Search FAISS index
        query_vector = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = index.search(query_vector, top_k * 2)
        
        # Filter by threshold and gather results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0 or idx >= len(metadata):
                continue
                
            similarity = float(dist)
            
            if similarity >= SIMILARITY_THRESHOLD:
                meta = metadata[idx]
                results.append({
                    "content": meta["text"],
                    "source": meta["source"],
                    "type": meta["type"],
                    "similarity": similarity,
                    "chunk_id": meta.get("chunk_id", 0)
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        logger.info(f"Found {len(results)} results above threshold {SIMILARITY_THRESHOLD}")
        
        return results[:top_k]
    except Exception as e:
        logger.error(f"Error searching FAISS: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


def generate_answer(question: str, context_chunks: List[dict]) -> dict:
    """Generate answer using Gemini with retrieved context"""
    try:
        logger.info(f"Generating answer for question: '{question[:50]}...'")
        
        if not context_chunks:
            return {
                "answer": "I couldn't find any relevant information in my knowledge base.",
                "links": []
            }
        
        # Build context from top chunks
        context_parts = []
        sources_used = {}
        
        for i, chunk in enumerate(context_chunks):
            source_url = chunk["source"]
            context_parts.append(f"[Source {i+1}]:\n{chunk['content']}\n")
            sources_used[i+1] = {
                "url": source_url,
                "snippet": chunk["content"][:150]
            }
        
        context = "\n".join(context_parts)
        
        # Create prompt
        prompt = f"""You are a helpful teaching assistant. Answer the student's question using ONLY the provided context below.

Context:
{context}

Question: {question}

Instructions:
1. Provide a clear, comprehensive answer based on the context
2. If the context doesn't contain enough information, say so
3. Reference specific sources when making claims (e.g., "According to Source 1...")
4. Be concise but thorough

Answer:"""

        # ✅ Updated for google-genai package
        logger.info("Calling Gemini API for answer generation")
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        answer_text = response.text
        logger.info(f"Generated answer (length: {len(answer_text)})")
        
        # Extract links from sources used
        links = []
        for source_num, source_info in sources_used.items():
            links.append({
                "url": source_info["url"],
                "text": source_info["snippet"]
            })
        
        return {
            "answer": answer_text,
            "links": links
        }
        
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """Main query endpoint"""
    try:
        logger.info(f"Received query: '{request.question[:50]}...'")
        
        # Get query embedding
        query_embedding = get_embedding(request.question)
        
        # Search for similar content
        similar_chunks = search_similar(query_embedding)
        
        # Generate answer
        result = generate_answer(request.question, similar_chunks)
        
        logger.info("Query processed successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in query endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "faiss_vectors": index.ntotal,
            "metadata_entries": len(metadata),
            "gemini_api_configured": bool(GEMINI_API_KEY)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VirtualTA RAG API",
        "version": "1.0",
        "endpoints": {
            "query": "/query",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
