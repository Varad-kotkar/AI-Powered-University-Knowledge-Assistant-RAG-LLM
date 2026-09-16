import os
from typing import List
from langgraph.graph import StateGraph, START, END
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_groq import ChatGroq
from schema import AssistantState, DocumentChunk, StudentContext
import numpy as np

load_dotenv()

# Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "mit_adt_university")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize components
print(f"Loading embedding model: {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)

print(f"Connecting to MongoDB: {DB_NAME}")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["university_documents"]

print(f"Initializing LLM: Groq")
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.1,
    max_tokens=1024
)


def prepare_query(state: AssistantState) -> AssistantState:
    """
    Prepare the query by integrating student context for better retrieval.
    This enhances relevance by adding academic context to the search.
    """
    question = state["question"]
    student_context = state.get("student_context")
    
    prepared_query = question
    
    if student_context:
        context_parts = []
        if student_context.get("program"):
            context_parts.append(f"Program: {student_context['program']}")
        if student_context.get("branch"):
            context_parts.append(f"Branch: {student_context['branch']}")
        if student_context.get("year"):
            context_parts.append(f"Year: {student_context['year']}")
        if student_context.get("semester"):
            context_parts.append(f"Semester: {student_context['semester']}")
        
        if context_parts:
            context_str = ", ".join(context_parts)
            prepared_query = f"{question} (Context: {context_str})"
    
    return {
        **state,
        "prepared_query": prepared_query
    }


def retrieve_documents(state: AssistantState) -> AssistantState:
    """
    Retrieve relevant document chunks from MongoDB using semantic search.
    Uses cosine similarity to find the most relevant chunks.
    """
    query = state["prepared_query"]
    student_context = state.get("student_context")
    
    # Generate query embedding
    query_embedding = model.encode(query, normalize_embeddings=True)
    
    # Build MongoDB query with optional context filters
    mongo_query = {}
    
    if student_context:
        # Add context-based filtering if available
        if student_context.get("program"):
            mongo_query["program"] = student_context["program"]
    
    # Retrieve all documents
    cursor = collection.find(mongo_query)
    documents = list(cursor)
    
    if not documents:
        return {
            **state,
            "retrieved_docs": [],
            "sources": []
        }
    
    # Calculate cosine similarity
    retrieved_docs = []
    for doc in documents:
        doc_embedding = np.array(doc["embedding"])
        similarity = np.dot(query_embedding, doc_embedding)
        
        retrieved_docs.append({
            "text": doc["text"],
            "source": doc["source"],
            "page": doc["page"],
            "category": doc["category"],
            "score": float(similarity)
        })
    
    # Sort by similarity score and take top 5
    retrieved_docs.sort(key=lambda x: x["score"], reverse=True)
    top_docs = retrieved_docs[:5]
    
    return {
        **state,
        "retrieved_docs": top_docs,
        "sources": top_docs
    }


def generate_answer(state: AssistantState) -> AssistantState:
    """
    Generate the final answer using the LLM with retrieved context.
    Includes strict grounding instructions and fallback for missing information.
    """
    question = state["question"]
    retrieved_docs = state["retrieved_docs"]
    sources = state["sources"]
    
    if not retrieved_docs:
        # Fallback when no relevant documents found
        fallback_answer = "I couldn't find this information in the available MIT-ADT university documents."
        return {
            **state,
            "answer": fallback_answer,
            "sources": []
        }
    
    # Build context from retrieved documents
    context_blocks = []
    for i, doc in enumerate(retrieved_docs, 1):
        context_block = f"[Source {i}: {doc['source']} Page {doc['page']}]\n{doc['text']}"
        context_blocks.append(context_block)
    
    context = "\n\n".join(context_blocks)
    
    # Build prompt with grounding instructions
    prompt = f"""You are an AI-powered academic assistant for MIT-ADT University, Pune, Maharashtra, India.

Your task is to answer the student's question using ONLY the provided MIT-ADT university documents below.

Context from MIT-ADT documents:
{context}

Student Question: {question}

Instructions:
1. Answer the question using ONLY the information provided in the context above.
2. Do NOT fabricate or invent any university-specific information.
3. If the information is not available in the context, state that clearly.
4. Format your answer clearly and professionally.
5. When citing information, reference the source document and page number.

Answer:"""

    # Generate answer
    response = llm.invoke(prompt)
    answer = response.content
    
    return {
        **state,
        "answer": answer
    }


# Build the LangGraph workflow
workflow = StateGraph(AssistantState)

# Add nodes
workflow.add_node("prepare_query", prepare_query)
workflow.add_node("retrieve_documents", retrieve_documents)
workflow.add_node("generate_answer", generate_answer)

# Define the workflow edges
workflow.add_edge(START, "prepare_query")
workflow.add_edge("prepare_query", "retrieve_documents")
workflow.add_edge("retrieve_documents", "generate_answer")
workflow.add_edge("generate_answer", END)

# Compile the graph
app = workflow.compile()


def ask_question(question: str, student_context: StudentContext = None) -> dict:
    """
    Main function to process a student question through the RAG pipeline.
    
    Args:
        question: The student's question
        student_context: Optional student academic context (program, branch, year, semester)
    
    Returns:
        Dictionary containing the answer and sources
    """
    # Initialize state
    state: AssistantState = {
        "question": question,
        "student_context": student_context,
        "prepared_query": "",
        "retrieved_docs": [],
        "answer": "",
        "sources": []
    }
    
    # Run the workflow
    result = app.invoke(state)
    
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "context_used": result["prepared_query"] if result["prepared_query"] != question else None
    }