from typing import TypedDict
from fastapi import APIRouter, HTTPException
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
)


class CalendarDTO(TypedDict):
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


router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/")
async def get_calendar(username: str):
    logger.debug(f"Getting calendar for user: {username}")
    events = get_user_events(username)

    if events is None:
        logger.warning(f"User not found: {username}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    logger.info(f"Retrieved {len(events)} events for user: {username}")
    return CalendarDTO(username=username, events=events)


@router.get("/events")
async def get_events_between_timestamps(username: str, from_timestamp: str, to_timestamp: str):
    logger.debug(f"Getting events between {from_timestamp} and {to_timestamp} for user: {username}")
    start = datetime.fromisoformat(from_timestamp)
    end = datetime.fromisoformat(to_timestamp)
    filtered_events = get_user_events_between_timestamps(username, start, end)

    if filtered_events is None:
        logger.warning(f"User not found: {username}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    logger.info(f"Retrieved {len(filtered_events)} events between timestamps for user: {username}")
    return CalendarDTO(username=username, events=filtered_events)


@router.post("/add")
async def add_event(data: AddEventDTO):
    logger.debug(f"Adding event for user: {data['username']}")
    from_ts = datetime.fromisoformat(data["from_timestamp"])
    to_ts = datetime.fromisoformat(data["to_timestamp"])
    event = db_add_event(data["username"], data["description"], from_ts, to_ts)

    if event is None:
        logger.warning(f"User not found: {data['username']}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    logger.info(f"Added event {event.id} for user: {data['username']}")
    return {"message": "Event added", "event_id": event.id}


@router.post("/remove")
async def remove_event(data: RemoveEventDTO):
    logger.debug(f"Removing event {data['event_id']} for user: {data['username']}")
    success = db_remove_event(data["username"], data["event_id"])

    if not success:
        logger.warning(f"User or event not found: user {data['username']}, event {data['event_id']}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User or event not found")
    logger.info(f"Removed event {data['event_id']} for user: {data['username']}")
    return {"message": "Event removed"}


@router.post("/edit")
async def edit_event(data: EditEventDTO):
    logger.debug(f"Editing event {data['event_id']} for user: {data['username']}")
    from_ts = datetime.fromisoformat(data["from_timestamp"])
    to_ts = datetime.fromisoformat(data["to_timestamp"])
    success = db_edit_event(data["username"], data["event_id"], data["description"], from_ts, to_ts)

    if not success:
        logger.warning(f"User or event not found: user {data['username']}, event {data['event_id']}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User or event not found")
    logger.info(f"Updated event {data['event_id']} for user: {data['username']}")
    return {"message": "Event updated"}
