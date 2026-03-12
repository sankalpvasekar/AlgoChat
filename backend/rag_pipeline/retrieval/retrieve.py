import pickle
import numpy as np
import os

# Build paths relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# Lazy-loaded globals
_model = None
_index = None
_chunks = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("Loading embedding model...")
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def get_index_and_chunks():
    global _index, _chunks
    if _index is None or _chunks is None:
        import faiss
        index_path = os.path.join(DATA_DIR, "faiss_index.bin")
        chunks_path = os.path.join(DATA_DIR, "chunks.pkl")

        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            print(f"WARNING: RAG assets not found at {DATA_DIR}. RAG retrieval will be disabled.")
            return None, None

        if _index is None:
            print(f"Loading FAISS index from {index_path}...")
            _index = faiss.read_index(index_path)
            
        if _chunks is None:
            print(f"Loading chunks from {chunks_path}...")
            with open(chunks_path, "rb") as f:
                _chunks = pickle.load(f)
                
    return _index, _chunks

def retrieve_top_chunks(query, top_k=3):
    model = get_model()
    index, chunks = get_index_and_chunks()

    if index is None or chunks is None:
        return ["RAG System is currently offline - missing index files."]

    # Convert query to embedding
    query_embedding = model.encode([query]).astype("float32")

    # Search in FAISS
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i in indices[0]:
        if i != -1 and i < len(chunks):
            results.append(chunks[i])

    return results

if __name__ == "__main__":
    # Test query
    query = "What is a binary search tree?"
    results = retrieve_top_chunks(query)
    for r in results:
        print(r)
        print("-" * 50)