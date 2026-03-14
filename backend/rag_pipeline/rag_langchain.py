import os
from dotenv import load_dotenv
import pickle

# Load API key
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))

# Lazy-loaded globals
_vectorstore = None
_qa_chain = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        import faiss
        from langchain_community.vectorstores import FAISS
        from langchain_community.docstore.in_memory import InMemoryDocstore
        from langchain_core.documents import Document
        from rag_pipeline.embeddings_api import CloudEmbedder
        from langchain_core.embeddings import Embeddings

        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
        index_path = os.path.join(data_dir, "faiss_index.bin")
        chunks_path = os.path.join(data_dir, "chunks.pkl")

        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            print("WARNING: FAISS assets missing. LangChain RAG disabled.")
            return None
        
        class HFCloudEmbeddings(Embeddings):
            def __init__(self):
                self.embedder = CloudEmbedder()
            def embed_documents(self, texts):
                return self.embedder.encode(texts, convert_to_numpy=False)
            def embed_query(self, text):
                embeddings = self.embedder.encode([text], convert_to_numpy=False)
                return embeddings[0] if embeddings else [0.0]*384

        embeddings = HFCloudEmbeddings()
        
        index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            chunks = pickle.load(f)

        docstore = InMemoryDocstore({str(i): Document(page_content=chunk, metadata={}) for i, chunk in enumerate(chunks)})
        index_to_docstore_id = {i: str(i) for i in range(len(chunks))}

        _vectorstore = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id
        )
    return _vectorstore

def get_qa_chain():
    global _qa_chain
    if _qa_chain is None:
        from langchain_groq import ChatGroq
        from langchain.chains import create_retrieval_chain
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

        vectorstore = get_vectorstore()
        if vectorstore is None:
            return None

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        system_template = """You are an experienced and patient computer science teacher who specializes in teaching Data Structures and Algorithms (DSA).
Goal: Teach like a human teacher in a classroom using an interactive Socratic method. DO NOT give long lecture-style explanations.

Strict Teaching Principles:
1. Short Chunks: Explain in medium-sized chunks (5–8 lines). Never give long paragraphs.
2. Mandatory Questions: After each chunk, pause and ask a curiosity, prediction, or reasoning question.
3. Teaching Loop:
   - Start with a real-life curiosity question.
   - Introduce concepts gradually (chunked).
   - Use diagrams for visualization (Stack, List, Tree, ASCII).
   - Ask for reasoning/predictions.
4. Formatting:
   - Explanation -> Diagram/Example -> Question -> STOP.
5. Visualization:
   - Use ASCII diagrams for stacks/lists/trees.
   - Also include a specialized `d3-json` block for frontend visualization.

Use the following context to answer the student's question:
{context}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template("{question}")
        ])

        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)
        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        _qa_chain = create_retrieval_chain(retriever, combine_docs_chain)
    return _qa_chain

# Exported interface
def invoke_rag(question):
    chain = get_qa_chain()
    if chain is None:
        return "RAG System is offline. Missing index files."
    return chain.invoke({"input": question})["answer"]

if __name__ == "__main__":
    while True:
        question = input("\nAsk Question: ")
        if question.lower() == "exit": break
        print("\nAnswer:\n", invoke_rag(question))