from typing import Literal, Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid

users = []


class Event(BaseModel):
    id: str
    description: str
    from_timestamp: datetime
    to_timestamp: datetime


class User(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    status: Literal["setup", "finished"]
    events: List[Event] = []


def create_user(user: User):
    users.append(user)


def get_user(username: str):
    for user in users:
        if user.username == username:
            return user
    return None


def add_event(username: str, description: str, from_timestamp: datetime, to_timestamp: datetime):
    user = get_user(username)
    if user is None:
        return None
    event = Event(
        id=str(uuid.uuid4()),
        description=description,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp
    )
    user.events.append(event)
    return event


def remove_event(username: str, event_id: str):
    user = get_user(username)
    if user is None:
        return False
    original_count = len(user.events)
    user.events = [e for e in user.events if e.id != event_id]
    return len(user.events) < original_count


def edit_event(username: str, event_id: str, description: str, from_timestamp: datetime, to_timestamp: datetime):
    user = get_user(username)
    if user is None:
        return False
    for event in user.events:
        if event.id == event_id:
            event.description = description
            event.from_timestamp = from_timestamp
            event.to_timestamp = to_timestamp
            return True
    return False


def get_user_events(username: str):
    user = get_user(username)
    if user is None:
        return None
    return user.events
