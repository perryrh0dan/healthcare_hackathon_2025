from typing import TypedDict
from fastapi import APIRouter, HTTPException
from loguru import logger
from http import HTTPStatus
from datetime import datetime
import uuid

from src.db import Event, get_user


class CalenderDTO(TypedDict):
    username: str
    events: list[Event]


class AddEventDTO(TypedDict):
    username: str
    description: str
    from_timestamp: str  # ISO format
    to_timestamp: str


class RemoveEventDTO(TypedDict):
    username: str
    event_id: str


class EditEventDTO(TypedDict):
    username: str
    event_id: str
    description: str
    from_timestamp: str
    to_timestamp: str


router = APIRouter(prefix="/calender", tags=["calender"])


@router.get("/")
async def get_calendar(username: str):
    logger.debug(f"Getting calendar for user: {username}")
    user = get_user(username)
    if user is None:
        logger.warning(f"User not found: {username}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    logger.info(f"Retrieved {len(user.events)} events for user: {username}")
    return CalenderDTO(username=username, events=user.events)


@router.post("/add")
async def add_event(data: AddEventDTO):
    logger.debug(f"Adding event for user: {data['username']}")
    user = get_user(data["username"])
    if user is None:
        logger.warning(f"User not found: {data['username']}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    event = Event(
        id=str(uuid.uuid4()),
        description=data["description"],
        from_timestamp=datetime.fromisoformat(data["from_timestamp"]),
        to_timestamp=datetime.fromisoformat(data["to_timestamp"]),
    )
    user.events.append(event)
    logger.info(f"Added event {event.id} for user: {data['username']}")
    return {"message": "Event added", "event_id": event.id}


@router.post("/remove")
async def remove_event(data: RemoveEventDTO):
    logger.debug(f"Removing event {data['event_id']} for user: {data['username']}")
    user = get_user(data["username"])
    if user is None:
        logger.warning(f"User not found: {data['username']}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    original_count = len(user.events)
    user.events = [e for e in user.events if e.id != data["event_id"]]
    if len(user.events) < original_count:
        logger.info(f"Removed event {data['event_id']} for user: {data['username']}")
    else:
        logger.warning(f"Event {data['event_id']} not found for user: {data['username']}")
    return {"message": "Event removed"}


@router.post("/edit")
async def edit_event(data: EditEventDTO):
    logger.debug(f"Editing event {data['event_id']} for user: {data['username']}")
    user = get_user(data["username"])
    if user is None:
        logger.warning(f"User not found: {data['username']}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    for event in user.events:
        if event.id == data["event_id"]:
            event.description = data["description"]
            event.from_timestamp = datetime.fromisoformat(data["from_timestamp"])
            event.to_timestamp = datetime.fromisoformat(data["to_timestamp"])
            logger.info(f"Updated event {data['event_id']} for user: {data['username']}")
            return {"message": "Event updated"}
    logger.warning(f"Event {data['event_id']} not found for user: {data['username']}")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Event not found")
