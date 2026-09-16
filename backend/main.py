from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from schema import QueryRequest, QueryResponse, StudentContext
from agentic_rag import ask_question
import os

app = FastAPI(
    title="AI-Powered University Knowledge Assistant | RAG & LLM",
    description="Academic Assistant for MIT-ADT University, Pune",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint with assistant metadata."""
    return {
        "status": "API is running live.",
        "assistant": "AI-Powered University Knowledge Assistant | RAG & LLM",
        "university": "MIT-ADT University, Pune, Maharashtra, India"
    }


@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    """
    Main query endpoint for asking questions about MIT-ADT University.
    
    Accepts a question and optional student context (program, branch, year, semester).
    Returns an answer with source citations from university documents.
    """
    # Convert student context from Pydantic model to dict if provided
    student_context_dict = None
    if request.student_context:
        student_context_dict = request.student_context.model_dump()
    
    # Process the question through the RAG pipeline
    result = ask_question(
        question=request.question,
        student_context=student_context_dict
    )
    
    # Convert sources to proper format
    sources = []
    for source in result["sources"]:
        sources.append({
            "text": source["text"],
            "source": source["source"],
            "page": source["page"],
            "category": source["category"],
            "score": source["score"]
        })
    
    return QueryResponse(
        answer=result["answer"],
        sources=sources,
        context_used=result["context_used"]
    )


# Mount static files for the frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend HTML page."""
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found. Please create frontend/index.html"}
