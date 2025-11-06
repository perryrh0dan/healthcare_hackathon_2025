from langchain.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from .clients.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
import json
from datetime import datetime
from .config import logger
from .db import add_event, remove_event, edit_event, get_user_events

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


@tool()
def get_calendar(username: str):
    """Get all events from a user's calendar."""
    logger.debug(f"Getting calendar for user: {username}")
    try:
        events = get_user_events(username)
        if events is None:
            logger.warning(f"User not found: {username}")
            return f"User {username} not found"
        if not events:
            return f"No events found for user {username}"
        event_list = []
        for event in events:
            event_list.append({
                "id": event.id,
                "description": event.description,
                "from_timestamp": event.from_timestamp.isoformat(),
                "to_timestamp": event.to_timestamp.isoformat()
            })
        logger.info(f"Retrieved {len(events)} events for user: {username}")
        return json.dumps({"username": username, "events": event_list})
    except Exception as e:
        logger.error(f"Error getting calendar for user {username}: {e}")
        return f"Error retrieving calendar: {str(e)}"


@tool()
def add_calendar_event(username: str, description: str, from_timestamp: str, to_timestamp: str):
    """Add a new event to a user's calendar. Timestamps should be in ISO format (e.g., '2025-11-07T10:00:00')."""
    logger.debug(f"Adding event for user: {username}")
    try:
        from_dt = datetime.fromisoformat(from_timestamp)
        to_dt = datetime.fromisoformat(to_timestamp)
        event = add_event(username, description, from_dt, to_dt)
        if event is None:
            logger.warning(f"User not found: {username}")
            return f"User {username} not found"
        logger.info(f"Added event {event.id} for user: {username}")
        return f"Successfully added event '{description}' with ID {event.id}"
    except ValueError as e:
        logger.error(f"Invalid timestamp format: {e}")
        return f"Invalid timestamp format. Use ISO format like '2025-11-07T10:00:00'"
    except Exception as e:
        logger.error(f"Error adding event for user {username}: {e}")
        return f"Error adding event: {str(e)}"


@tool()
def remove_calendar_event(username: str, event_id: str):
    """Remove an event from a user's calendar by event ID."""
    logger.debug(f"Removing event {event_id} for user: {username}")
    try:
        success = remove_event(username, event_id)
        if not success:
            logger.warning(f"Event {event_id} not found for user: {username}")
            return f"Event {event_id} not found for user {username}"
        logger.info(f"Removed event {event_id} for user: {username}")
        return f"Successfully removed event {event_id}"
    except Exception as e:
        logger.error(f"Error removing event {event_id} for user {username}: {e}")
        return f"Error removing event: {str(e)}"


@tool()
def edit_calendar_event(username: str, event_id: str, description: str, from_timestamp: str, to_timestamp: str):
    """Edit an existing event in a user's calendar. Timestamps should be in ISO format."""
    logger.debug(f"Editing event {event_id} for user: {username}")
    try:
        from_dt = datetime.fromisoformat(from_timestamp)
        to_dt = datetime.fromisoformat(to_timestamp)
        success = edit_event(username, event_id, description, from_dt, to_dt)
        if not success:
            logger.warning(f"Event {event_id} not found for user: {username}")
            return f"Event {event_id} not found for user {username}"
        logger.info(f"Updated event {event_id} for user: {username}")
        return f"Successfully updated event {event_id}"
    except ValueError as e:
        logger.error(f"Invalid timestamp format: {e}")
        return f"Invalid timestamp format. Use ISO format like '2025-11-07T10:00:00'"
    except Exception as e:
        logger.error(f"Error editing event {event_id} for user {username}: {e}")
        return f"Error editing event: {str(e)}"
