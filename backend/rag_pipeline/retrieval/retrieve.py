import faiss
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("data/processed/faiss_index.bin")

# Load text chunks
with open("data/processed/chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

# FAISS index and chunks loaded
# print("FAISS index loaded!")
# print("Total chunks:", len(chunks))


def retrieve_top_chunks(query, top_k=3):
    # Convert query to embedding
    query_embedding = model.encode([query]).astype("float32")

    # Search in FAISS
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i in indices[0]:
        results.append(chunks[i])

    return results

# Test query
query = "What is a binary search tree?"

results = retrieve_top_chunks(query)

# print("\nTop Results:\n")

for r in results:
    print(r)
    print("-"*50)