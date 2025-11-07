from langchain_core.vectorstores import InMemoryVectorStore
from .clients.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
from .config import logger
from datetime import datetime, timedelta
from .db import Answer, DailyAnswers, get_user_conversations, get_user, User
from typing import List, Dict, Optional
from .db import Event
from fastapi import HTTPException, Request
from http import HTTPStatus

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


def get_recent_messages(username: str):
    user_convs = get_user_conversations(username)
    all_messages = []
    for conv in user_convs.values():
        all_messages.extend(conv.messages)
    now = datetime.now()
    recent = [
        msg
        for msg in all_messages
        if msg.timestamp and now - msg.timestamp < timedelta(hours=24)
    ]
    return recent


def calculate_streak(daily_answers: List[DailyAnswers]) -> int:
    """Calculate consecutive days streak of daily answers from today backwards."""
    if not daily_answers:
        return 0

    # Sort by date descending (most recent first)
    sorted_answers = sorted(daily_answers, key=lambda x: x.date, reverse=True)
    streak = 0
    current_date = datetime.now().date()

    for entry in sorted_answers:
        entry_date = datetime.fromisoformat(entry.date).date()
        if entry_date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        elif entry_date == current_date - timedelta(days=1):
            streak += 1
            current_date = entry_date - timedelta(days=1)
        else:
            break
    return streak


def get_next_appointment(events: List[Event]) -> Optional[Event]:
    """Find the next upcoming appointment/event."""
    now = datetime.now()
    future_events = [e for e in events if e.from_timestamp > now]
    return min(future_events, key=lambda e: e.from_timestamp) if future_events else None


def get_current_user(request: Request) -> User:
    """Dependency to extract and validate current user from cookie."""
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Not authenticated"
        )

    user = get_user(username)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="User not found"
        )

    return user
