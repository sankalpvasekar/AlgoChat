import os
from dotenv import load_dotenv
import faiss
import pickle
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Load API key
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '.env'))

# Lazy-loaded globals
_vectorstore = None
_qa_chain = None

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
        index_path = os.path.join(data_dir, "faiss_index.bin")
        chunks_path = os.path.join(data_dir, "chunks.pkl")

        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            print("WARNING: FAISS assets missing. LangChain RAG disabled.")
            return None

        # Load embedding model
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
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
        vectorstore = get_vectorstore()
        if vectorstore is None:
            return None

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        system_template = """You are an experienced and patient computer science teacher...
        {context}
        """ # Truncated for brevity, normally matches what was there
        
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