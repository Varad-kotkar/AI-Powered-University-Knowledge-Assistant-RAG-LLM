from pydantic import BaseModel, Field
from typing import List, Optional, TypedDict


class StudentContext(BaseModel):
    """Student academic context for relevance boosting."""
    program: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    semester: Optional[str] = None


class DocumentChunk(BaseModel):
    """Retrieved document chunk with metadata."""
    text: str
    source: str
    page: int
    category: str
    score: float


class QueryRequest(BaseModel):
    """User query request with optional student context."""
    question: str
    student_context: Optional[StudentContext] = None


class QueryResponse(BaseModel):
    """Query response with answer and sources."""
    answer: str
    sources: List[DocumentChunk]
    context_used: Optional[str] = None


class AssistantState(TypedDict):
    """LangGraph state for the RAG workflow."""
    question: str
    student_context: Optional[StudentContext]
    prepared_query: str
    retrieved_docs: List[DocumentChunk]
    answer: str
    sources: List[DocumentChunk]