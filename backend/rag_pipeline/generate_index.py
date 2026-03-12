import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

def generate_minimal_index():
    print("Generating minimal FAISS index for deployment...")
    
    # 1. Define sample data
    chunks = [
        "AlgoChat is an AI-powered tutor for Data Structures and Algorithms.",
        "It uses RAG (Retrieval Augmented Generation) to provide context-aware answers.",
        "The Socratic method is used to guide students instead of just giving answers."
    ]
    
    # 2. Load model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    # 3. Create embeddings
    embeddings = model.encode(chunks).astype("float32")
    
    # 4. Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # 5. Save assets
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    index_path = os.path.join(output_dir, "faiss_index.bin")
    chunks_path = os.path.join(output_dir, "chunks.pkl")
    
    faiss.write_index(index, index_path)
    with open(chunks_path, "wb") as f:
        pickle.dump(chunks, f)
        
    print(f"SUCCESS: Saved index and chunks to {output_dir}")

if __name__ == "__main__":
    generate_minimal_index()
