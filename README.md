# AI-Powered University Knowledge Assistant | RAG & LLM

**An AI-powered academic assistant for MIT-ADT University students.**

Developed an AI-powered academic assistant for MIT-ADT University that enables students to ask natural-language questions across syllabus, academic documents, notices, and previous-year question papers. The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant university information and an LLM to generate context-based responses.

---

## Overview

Students often need to search through multiple academic documents, syllabus files, notices, and previous-year question papers to find information about their courses, exams, and university policies. This assistant simplifies that process by allowing students to ask questions in natural language and receive accurate, context-aware answers backed by official university documents.

---

## Problem Statement

 University students face challenges when searching for:
- Syllabus information for specific subjects and semesters
- Academic regulations and course structures
- Examination notices and important deadlines
- Previous-year question papers (PYQs) for exam preparation
- University policies and guidelines

Finding this information typically requires navigating multiple documents, websites, and PDFs, which is time-consuming and inefficient.

---

## Solution

The AI-Powered University Knowledge Assistant uses Retrieval-Augmented Generation (RAG) to:
1. **Ingest** MIT-ADT university documents (PDFs, text files) into a knowledge base
2. **Process** documents by extracting text, chunking, and generating embeddings
3. **Retrieve** relevant document chunks using semantic search
4. **Generate** context-aware answers using an LLM
5. **Cite** sources with document names and page numbers for verification

Students can simply ask questions like:
- "What is the DBMS syllabus?"
- "Find previous-year papers for Data Mining."
- "What does the latest examination notice say?"
- "What subjects are included in my semester?"

---

## Key Features

- **Natural-language academic queries** - Ask questions in plain English
- **MIT-ADT-specific knowledge base** - Tailored to university documents
- **RAG-based question answering** - Grounded responses from official documents
- **Syllabus search** - Find course syllabi quickly
- **Academic document search** - Access regulations and guidelines
- **Notice search** - Stay updated with university announcements
- **PYQ search** - Find previous-year question papers
- **Student academic context** - Program, branch, year, semester for relevance
- **Semantic search** - Find relevant information using embeddings
- **Source information** - Citations with document names and page numbers

---

## How RAG Works

The RAG pipeline follows these steps:

```
MIT-ADT Documents (PDFs)
       ↓
Document Ingestion (ingest.py)
       ↓
Text Extraction (pypdf)
       ↓
Text Chunking (RecursiveCharacterTextSplitter)
       ↓
Sentence Transformers (all-MiniLM-L6-v2)
       ↓
Embeddings + Chunks Stored in MongoDB
       ↓
Student Question + Student Context
       ↓
Semantic Retrieval (Cosine Similarity)
       ↓
Relevant Document Chunks
       ↓
LLM (Groq Llama 3.1)
       ↓
Final Answer + Document Sources
```

### Step-by-Step Explanation

1. **Document Ingestion**: PDF files are loaded from the `data/mit_adt/` directory
2. **Text Extraction**: Text and page numbers are extracted from each PDF
3. **Text Chunking**: Large documents are split into smaller chunks (700 characters with 100 overlap) for better retrieval
4. **Embeddings**: Each chunk is converted to a numerical vector using Sentence Transformers
5. **Storage**: Chunks and embeddings are stored in MongoDB for fast retrieval
6. **Query Processing**: Student questions are converted to embeddings using the same model
7. **Semantic Retrieval**: The system finds the most similar document chunks using cosine similarity
8. **Answer Generation**: The LLM generates a response using the retrieved context
9. **Source Citation**: The answer includes document names and page numbers for verification

---

## Student Context

The assistant supports student academic context to improve retrieval relevance:

**Program**: B.Tech, M.Tech, BCA, MCA  
**Branch**: AI & Data Analytics, CSE, IT, Mechanical, Civil  
**Year**: 1st, 2nd, 3rd, 4th  
**Semester**: 1st through 8th

When a student provides their context (e.g., B.Tech, AI & Data Analytics, 3rd Year, Semester 5), the system:
- Integrates this context into the search query
- Prioritizes documents relevant to their program and semester
- Provides more targeted and accurate answers

Example: If a student asks "What is my syllabus?" with context B.Tech AI & Data Analytics Semester 5, the system will retrieve syllabus documents specific to that program and semester.

---

## Technology Stack

- **Python** - Core programming language
- **LangChain** - Document loading, text splitting, prompt handling
- **LangGraph** - Workflow orchestration for the RAG pipeline
- **MongoDB** - Document storage and retrieval
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **LLM** - Groq (Llama 3.1) for response generation
- **FastAPI** - Backend API framework
- **PyPDF** - PDF text extraction

---

## Example Questions

- "What is the DBMS syllabus?"
- "Find previous-year papers for Data Mining."
- "What does the latest examination notice say?"
- "What subjects are included in my semester?"
- "Explain this academic document."
- "What is the attendance policy?"
- "Find notices about examinations."

---

## Project Structure

```text
project/
├── backend/
│   ├── main.py              # FastAPI application with API endpoints
│   ├── agentic_rag.py       # LangGraph RAG workflow
│   └── schema.py            # Pydantic models for API and state
├── frontend/
│   ├── index.html           # Web interface
│   ├── styles.css           # Styling
│   └── app.js               # Frontend logic
├── data/
│   └── mit_adt/
│       ├── syllabus/        # Syllabus documents
│       ├── academics/       # Academic regulations
│       ├── notices/         # University notices
│       ├── pyqs/            # Previous-year question papers
│       └── university/      # General university information
├── ingest.py                # Document ingestion pipeline
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd AI-Powered-University-Knowledge-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=mit_adt_university

# LLM Configuration
GROQ_API_KEY=your_groq_api_key_here

# Embedding Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Text Chunking Configuration
CHUNK_SIZE=700
CHUNK_OVERLAP=100
```

You can use `.env.example` as a template.

---

## Running the Project

### 1. Add MIT-ADT Documents

Place your MIT-ADT university documents in the appropriate directories:

```text
data/mit_adt/syllabus/      # Syllabus PDFs
data/mit_adt/academics/     # Academic regulations
data/mit_adt/notices/       # Examination and university notices
data/mit_adt/pyqs/          # Previous-year question papers
data/mit_adt/university/    # General university information
```

### 2. Run Document Ingestion

Process the documents and store them in MongoDB:

```bash
python ingest.py
```

This will:
- Scan all PDF and text files in the data directories
- Extract text and page numbers
- Chunk the text
- Generate embeddings
- Store everything in MongoDB

### 3. Start the Backend Server

```bash
uvicorn backend.main:app --reload
```

The server will start on `http://localhost:8000`

### 4. Access the Web Interface

Open your browser and navigate to:

```
http://localhost:8000/
```

You can also test the API directly:

- **Health Check**: `GET http://localhost:8000/health`
- **Query Endpoint**: `POST http://localhost:8000/query`

---

## API Endpoints

### Health Check

**GET** `/health`

Returns assistant status and metadata:

```json
{
  "status": "API is running live.",
  "assistant": "AI-Powered University Knowledge Assistant | RAG & LLM",
  "university": "MIT-ADT University, Pune, Maharashtra, India"
}
```

### Query Endpoint

**POST** `/query`

Request body:

```json
{
  "question": "What is the DBMS syllabus?",
  "student_context": {
    "program": "B.Tech",
    "branch": "AI & Data Analytics",
    "year": "3rd",
    "semester": "5th"
  }
}
```

Response:

```json
{
  "answer": "The DBMS syllabus includes...",
  "sources": [
    {
      "text": "Database Management Systems syllabus...",
      "source": "DBMS_Syllabus.pdf",
      "page": 4,
      "category": "syllabus",
      "score": 0.85
    }
  ],
  "context_used": "What is the DBMS syllabus? (Context: Program: B.Tech, Branch: AI & Data Analytics, Year: 3rd, Semester: 5th)"
}
```

---

## LangGraph Workflow

The assistant uses LangGraph to organize the sequential steps of the question-answering workflow:

```
[START]
   ↓
[prepare_query]       <-- Injects student context into query
   ↓
[retrieve_documents]  <-- Embeds query and retrieves top-k chunks from MongoDB
   ↓
[generate_answer]     <-- Formats prompt with context, invokes LLM, extracts sources
   ↓
 [END]
```

This creates an observable state pipeline that:
1. Prepares context-aware queries
2. Retrieves relevant document chunks from MongoDB
3. Generates grounded responses with source citations

---

## Limitations

- The assistant can only answer reliably from the available MIT-ADT documents
- Information not present in the knowledge base will result in a fallback response
- Document quality and completeness affect answer accuracy
- The system requires MongoDB connection and Groq API key to function
- Embeddings are generated locally, which may require sufficient computational resources

---

## Future Improvements

- Add support for more document types (Word, Excel, etc.)
- Implement hybrid search combining semantic and keyword search
- Add document versioning and update tracking
- Implement user authentication and personalization
- Add multilingual support
- Create mobile application
- Implement caching for frequently asked questions

---

## Interview Walkthrough Guide

### Key Talking Points

1. **Problem Solved**: Students struggle to find information across multiple university documents
2. **Solution**: RAG-based assistant that retrieves relevant information and generates answers
3. **Architecture**: Simple, explainable pipeline with clear stages
4. **Technologies**: Python, LangChain, LangGraph, MongoDB, Sentence Transformers, Groq
5. **Student Context**: Program, branch, year, semester improve retrieval relevance
6. **Source Citation**: Answers include document names and page numbers for verification

### Resume Bullet Support

This project supports the following resume claims:

1. **"Developed an AI-powered academic assistant for natural-language queries across syllabus, academic documents, notices, and previous-year question papers (PYQs)."**
   - Implemented: Document ingestion, RAG pipeline, web interface

2. **"Implemented a Retrieval-Augmented Generation (RAG) pipeline covering document ingestion, text chunking, embeddings, semantic retrieval, and LLM response generation."**
   - Implemented: Complete RAG pipeline with all stages

3. **"Integrated program, branch, year, and semester context to improve retrieval relevance and provide context-aware answers."**
   - Implemented: Student context selectors and context-aware query preparation

---

## License

This project is developed for educational and demonstration purposes.

---

## Contact

For questions or feedback about this project, please contact the development team.
