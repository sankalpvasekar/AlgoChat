import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

# Load API key
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))

# Load embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

import faiss
import pickle
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document

# Load FAISS index and chunks
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
index = faiss.read_index(os.path.join(data_dir, "faiss_index.bin"))

with open(os.path.join(data_dir, "chunks.pkl"), "rb") as f:
    chunks = pickle.load(f)

# Create a proper InMemoryDocstore mapping IDs to chunks
docstore = InMemoryDocstore(
    {str(i): Document(page_content=chunk, metadata={}) for i, chunk in enumerate(chunks)}
)
index_to_docstore_id = {i: str(i) for i in range(len(chunks))}

# Wrap in LangChain FAISS object
vectorstore = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=docstore,
    index_to_docstore_id=index_to_docstore_id
)

# Create retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Socratic CS Teacher Persona
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

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

# Load Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3
)

# Create RAG chain
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

combine_docs_chain = create_stuff_documents_chain(llm, prompt)
qa_chain = create_retrieval_chain(retriever, combine_docs_chain)

# Chat loop
if __name__ == "__main__":
    while True:
        question = input("\nAsk Question: ")
        if question.lower() == "exit":
            break
        
        response = qa_chain.invoke({"input": question})
        print("\nAnswer:\n")
        print(response["answer"])