from langchain.tools import tool
from ..config import logger
from ..utils import vector_store


@tool()
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    logger.debug(f"Retrieving context for query: {query}")
    try:
        retrieved_docs = vector_store.similarity_search(query, k=2)
        logger.debug(f"Retrieved {len(retrieved_docs)} documents")
        if not retrieved_docs:
            logger.warning("No documents retrieved for query")
        serialized = "\n\n".join((f"Source: {doc.metadata}\nContent: {doc.page_content}") for doc in retrieved_docs)
        return serialized
    except Exception as e:
        logger.error(f"Error during retrieval: {e}")
        return "Error retrieving context"