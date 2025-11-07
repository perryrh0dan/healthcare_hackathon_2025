from typing import TypedDict
from fastapi import APIRouter, HTTPException, Depends
from ..config import logger
from http import HTTPStatus
from datetime import datetime
from src.db import (
    Event,
    get_user_events,
    add_event as db_add_event,
    remove_event as db_remove_event,
    edit_event as db_edit_event,
    get_user_events_between_timestamps,
    User,
)
from ..utils import get_current_user


class CalendarDTO(TypedDict):
    events: list[Event]


class AddEventDTO(TypedDict):
    description: str
    from_timestamp: str  # ISO format
    to_timestamp: str


class RemoveEventDTO(TypedDict):
    event_id: str


class EditEventDTO(TypedDict):
    event_id: str
    description: str
    from_timestamp: str
    to_timestamp: str


router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/")
async def get_calendar(user: User = Depends(get_current_user)):
    logger.debug(f"Getting calendar for user: {user.username}")
    events = get_user_events(user.username)

    logger.info(f"Retrieved {len(events)} events for user: {user.username}")
    return CalendarDTO(events=events)


@router.get("/events")
async def get_events_between_timestamps(from_timestamp: str, to_timestamp: str, user: User = Depends(get_current_user)):
    logger.debug(f"Getting events between {from_timestamp} and {to_timestamp} for user: {user.username}")
    start = datetime.fromisoformat(from_timestamp)
    end = datetime.fromisoformat(to_timestamp)
    filtered_events = get_user_events_between_timestamps(user.username, start, end)

    logger.info(f"Retrieved {len(filtered_events)} events between timestamps for user: {user.username}")
    return CalendarDTO(events=filtered_events)


@router.post("/add")
async def add_event(data: AddEventDTO, user: User = Depends(get_current_user)):
    logger.debug(f"Adding event for user: {user.username}")
    from_ts = datetime.fromisoformat(data["from_timestamp"])
    to_ts = datetime.fromisoformat(data["to_timestamp"])
    event = db_add_event(user.username, data["description"], from_ts, to_ts)

    logger.info(f"Added event {event.id} for user: {user.username}")
    return {"message": "Event added", "event_id": event.id}


@router.post("/remove")
async def remove_event(data: RemoveEventDTO, user: User = Depends(get_current_user)):
    logger.debug(f"Removing event {data['event_id']} for user: {user.username}")
    success = db_remove_event(user.username, data["event_id"])

    if not success:
        logger.warning(f"User or event not found: user {user.username}, event {data['event_id']}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User or event not found")
    logger.info(f"Removed event {data['event_id']} for user: {user.username}")
    return {"message": "Event removed"}


@router.post("/edit")
async def edit_event(data: EditEventDTO, user: User = Depends(get_current_user)):
    logger.debug(f"Editing event {data['event_id']} for user: {user.username}")
    from_ts = datetime.fromisoformat(data["from_timestamp"])
    to_ts = datetime.fromisoformat(data["to_timestamp"])
    success = db_edit_event(user.username, data["event_id"], data["description"], from_ts, to_ts)

    if not success:
        logger.warning(f"User or event not found: user {user.username}, event {data['event_id']}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User or event not found")
    logger.info(f"Updated event {data['event_id']} for user: {user.username}")
    return {"message": "Event updated"}
