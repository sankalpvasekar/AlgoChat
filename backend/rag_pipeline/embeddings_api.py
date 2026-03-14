import os
import requests
import time
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

def query_hf_embeddings(texts):
    """
    Calls HuggingFace Inference API to get embeddings for a list of texts.
    """
    headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}
    payload = {"inputs": texts, "options": {"wait_for_model": True}}
    
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 503:
                # Model is loading
                print(f"HuggingFace model is loading, retrying in 5s... (Attempt {attempt+1})")
                time.sleep(5)
                continue
            else:
                print(f"HF API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"HF Connection Error: {e}")
            time.sleep(1)
            
    return None

class CloudEmbedder:
    """
    Mock-like object that replaces SentenceTransformer but uses the API.
    """
    def encode(self, texts, convert_to_numpy=True, **kwargs):
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = query_hf_embeddings(texts)
        if embeddings is None:
            # Fallback to zeros if API fails so the app doesn't crash completely
            import numpy as np
            return np.zeros((len(texts), 384)) if convert_to_numpy else [[0.0]*384]*len(texts)
            
        if convert_to_numpy:
            import numpy as np
            return np.array(embeddings)
        return embeddings
