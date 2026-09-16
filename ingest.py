import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
import numpy as np

load_dotenv()

# Configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "mit_adt_university")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

DATA_DIR = Path("data/mit_adt")

# Initialize embedding model
print(f"Loading embedding model: {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)

# Initialize MongoDB connection
print(f"Connecting to MongoDB: {DB_NAME}")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["university_documents"]

# Initialize text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
)


def extract_text_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """Extract text and page numbers from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        documents = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            if text.strip():
                documents.append({
                    "text": text,
                    "page": page_num
                })
        
        return documents
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return []


def extract_text_from_txt(txt_path: Path) -> List[Dict[str, Any]]:
    """Extract text from a text file."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return [{"text": text, "page": 1}]
    except Exception as e:
        print(f"Error reading TXT {txt_path}: {e}")
        return []


def get_category_from_path(file_path: Path) -> str:
    """Extract category from the file path (syllabus, academics, notices, pyqs, university)."""
    parent_dir = file_path.parent.name
    if parent_dir in ["syllabus", "academics", "notices", "pyqs", "university"]:
        return parent_dir
    return "general"


def process_file(file_path: Path, category: str) -> List[Dict[str, Any]]:
    """Process a single file and return chunks with metadata."""
    print(f"Processing: {file_path}")
    
    # Extract text based on file type
    if file_path.suffix.lower() == '.pdf':
        documents = extract_text_from_pdf(file_path)
    elif file_path.suffix.lower() == '.txt':
        documents = extract_text_from_txt(file_path)
    else:
        print(f"Skipping unsupported file type: {file_path.suffix}")
        return []
    
    # Chunk documents
    chunks = []
    for doc in documents:
        text_chunks = text_splitter.split_text(doc["text"])
        for chunk_idx, chunk in enumerate(text_chunks):
            chunks.append({
                "text": chunk,
                "source": file_path.name,
                "page": doc["page"],
                "category": category,
                "chunk_index": chunk_idx
            })
    
    return chunks


def generate_embeddings(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate embeddings for all chunks."""
    print(f"Generating embeddings for {len(chunks)} chunks...")
    
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, normalize_embeddings=True)
    
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding.tolist()
    
    return chunks


def store_in_mongodb(chunks: List[Dict[str, Any]]) -> None:
    """Store chunks in MongoDB."""
    print(f"Storing {len(chunks)} chunks in MongoDB...")
    
    # Clear existing documents from the same source files
    source_files = set(chunk["source"] for chunk in chunks)
    collection.delete_many({"source": {"$in": list(source_files)}})
    
    # Insert new chunks
    if chunks:
        collection.insert_many(chunks)
        print(f"Successfully inserted {len(chunks)} chunks")
    else:
        print("No chunks to insert")


def ingest_directory(directory: Path) -> None:
    """Ingest all supported files from a directory."""
    if not directory.exists():
        print(f"Directory does not exist: {directory}")
        return
    
    category = get_category_from_path(directory)
    all_chunks = []
    
    # Find all PDF and TXT files
    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt']:
            chunks = process_file(file_path, category)
            all_chunks.extend(chunks)
    
    if all_chunks:
        # Generate embeddings
        chunks_with_embeddings = generate_embeddings(all_chunks)
        
        # Store in MongoDB
        store_in_mongodb(chunks_with_embeddings)
    else:
        print(f"No supported files found in {directory}")


def main():
    """Main ingestion function."""
    print("=" * 60)
    print("MIT-ADT University Document Ingestion")
    print("=" * 60)
    
    # Check if data directory exists
    if not DATA_DIR.exists():
        print(f"Data directory does not exist: {DATA_DIR}")
        print("Please create the directory and add MIT-ADT documents.")
        return
    
    # Ingest each category
    categories = ["syllabus", "academics", "notices", "pyqs", "university"]
    
    for category in categories:
        category_dir = DATA_DIR / category
        print(f"\nProcessing category: {category}")
        print("-" * 40)
        ingest_directory(category_dir)
    
    print("\n" + "=" * 60)
    print("Ingestion completed!")
    print("=" * 60)
    
    # Print statistics
    total_docs = collection.count_documents({})
    print(f"Total documents in MongoDB: {total_docs}")


if __name__ == "__main__":
    main()
