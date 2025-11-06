from langchain_core.vectorstores import InMemoryVectorStore
from .clients.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
from .config import logger

embeddings = Embeddings()

vector_store = InMemoryVectorStore(embeddings.embeddings)

pdf_paths = ["pdfs/test.pdf"]
docs = []

for pdf_path in pdf_paths:
    try:
        if not os.path.exists(pdf_path):
            logger.error(f"PDF not found: {pdf_path}")
            continue
        loader = PyPDFLoader(pdf_path)
        loaded_docs = loader.load()
        docs.extend(loaded_docs)
        logger.info(f"Loaded {len(loaded_docs)} documents from {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to load PDF {pdf_path}: {e}")
        continue


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
    add_start_index=True,
)

all_splits = text_splitter.split_documents(docs)
logger.info(f"Split documents into {len(all_splits)} chunks")

try:
    document_ids = vector_store.add_documents(documents=all_splits)
    logger.info(f"Added {len(document_ids)} documents to vector store")
except Exception as e:
    logger.error(f"Failed to add documents to vector store: {e}")
    raise