import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------- SETTINGS ----------------
processed_folder = r"data/processed"
embedding_model_name = "all-MiniLM-L6-v2"
batch_size = 100  # adjust for memory efficiency

# Load the embedding model
model = SentenceTransformer(embedding_model_name)

# Load your preprocessed chunks
def load_chunks(filename):
    with open(os.path.join(processed_folder, filename), "r", encoding="utf-8") as f:
        return [chunk.strip() for chunk in f.read().split("\n\n") if chunk.strip()]

gfg_chunks = load_chunks("gfg_chunks.txt")
github_chunks = load_chunks("github_chunks.txt")

all_chunks = gfg_chunks + github_chunks
print(f"Total chunks: {len(all_chunks)}")

# ---------------- CREATE EMBEDDINGS ----------------
embeddings = []
for i in range(0, len(all_chunks), batch_size):
    batch = all_chunks[i:i+batch_size]
    batch_embeddings = model.encode(batch, convert_to_numpy=True)
    embeddings.append(batch_embeddings)
    print(f"Processed {i+len(batch)} / {len(all_chunks)} chunks")

embeddings = np.vstack(embeddings)  # shape: (total_chunks, embedding_dim)
print(f"Embeddings shape: {embeddings.shape}")

# ---------------- STORE IN FAISS ----------------
# ---------------- STORE IN FAISS ----------------
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)  # L2 distance for similarity search
index.add(embeddings.astype("float32"))

# Save FAISS index and chunks mapping
faiss_index_path = os.path.join(processed_folder, "faiss_index.bin")
faiss.write_index(index, faiss_index_path)

chunks_path = os.path.join(processed_folder, "chunks.pkl")
with open(chunks_path, "wb") as f:
    pickle.dump(all_chunks, f)

print(f"FAISS index saved at: {faiss_index_path}")
print(f"Chunks mapping saved at: {chunks_path}")