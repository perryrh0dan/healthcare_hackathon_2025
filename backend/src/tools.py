from langchain.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from .embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
import json

embeddings = Embeddings()

vector_store = InMemoryVectorStore(embeddings.embeddings)

pdf_paths = ["pdfs/test.pdf"]
docs = []

for pdf_path in pdf_paths:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    docs.extend(loader.load())


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    add_start_index=True,
)

all_splits = text_splitter.split_documents(docs)

document_ids = vector_store.add_documents(documents=all_splits)


@tool()
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join((f"Source: {doc.metadata}\nContent: {doc.page_content}") for doc in retrieved_docs)
    return serialized
