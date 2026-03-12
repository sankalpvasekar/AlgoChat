import os
from pathlib import Path
import re

# ---------- SETTINGS ----------
chunk_size = 1000   # characters per chunk
overlap = 200       # overlap between chunks

# Paths to raw data (use absolute paths to avoid path issues)
gfg_folder = r"C:\Users\DDR\Documents\Django\GEN_AI_ASSISTANT\backend\data\raw\geeksforgeeks"
github_folder = r"C:\Users\DDR\Documents\Django\GEN_AI_ASSISTANT\backend\data\raw\github"

# Output folder
processed_folder = r"C:\Users\DDR\Documents\Django\GEN_AI_ASSISTANT\backend\data\processed"
os.makedirs(processed_folder, exist_ok=True)

def clean_text(text, is_python=False):
    """Clean text by removing extra spaces, newlines, and Python comments/docstrings"""
    if is_python:
        # remove Python comments
        text = re.sub(r"#.*", "", text)
        # remove docstrings
        text = re.sub(r'"""[\s\S]*?"""', "", text)
        text = re.sub(r"'''[\s\S]*?'''", "", text)
    # normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunk_text(text, size=chunk_size, overlap=overlap):
    """Split text into chunks with overlap"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

def preprocess_folder(folder_path, extensions, is_python=False):
    """Preprocess files in a folder with given extensions"""
    all_chunks = []
    folder_path = Path(folder_path)
    
    for file in folder_path.rglob("*"):
        print("Found file:", file)  # debug: list all files
        if file.suffix in extensions and "init" not in file.name.lower() and "readme" not in file.name.lower():
            print("Processing:", file)  # debug: files being processed
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    text = clean_text(text, is_python)
                    chunks = chunk_text(text)
                    all_chunks.extend(chunks)
            except Exception as e:
                print(f"Failed to process {file}: {e}")
    
    return all_chunks

# ---------- PROCESS ----------
print("Preprocessing GeeksforGeeks data...")
gfg_chunks = preprocess_folder(gfg_folder, [".txt"], is_python=False)

print("Preprocessing GitHub data...")
github_chunks = preprocess_folder(github_folder, [".py"], is_python=True)

# Save all chunks
with open(os.path.join(processed_folder, "gfg_chunks.txt"), "w", encoding="utf-8") as f:
    for chunk in gfg_chunks:
        f.write(chunk + "\n\n")

with open(os.path.join(processed_folder, "github_chunks.txt"), "w", encoding="utf-8") as f:
    for chunk in github_chunks:
        f.write(chunk + "\n\n")

print("Preprocessing completed!")
print(f"Total chunks from GFG: {len(gfg_chunks)}")
print(f"Total chunks from GitHub: {len(github_chunks)}")