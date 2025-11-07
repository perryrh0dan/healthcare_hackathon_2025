from typing import Literal, Optional, List
from pydantic import BaseModel, create_model
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
    height: Optional[int] = None
    gender: Optional[Literal["male", "female", "other"]] = "other"
    status: Literal["setup", "finished"]
    allergies: Optional[str] = None
    issues: Optional[str] = None
    goal: Optional[str] = None
    events: List[Event] = []


class UpdateUser(User):
    password: Optional[str] = None


def update_user(update: UpdateUser):
    user = get_user(update.username)
    if user is None:
        raise RuntimeError()

    global users
    users = [user for user in users if user.username != user.username]

    update.password = user.password

    users.append(update)


def create_user(user: User):
    users.append(user)


def get_user(username: str):
    for user in users:
        if user.username == username:
            return user
    return None


def add_event(
    username: str, description: str, from_timestamp: datetime, to_timestamp: datetime
):
    user = get_user(username)
    if user is None:
        return None
    event = Event(
        id=str(uuid.uuid4()),
        description=description,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
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


def edit_event(
    username: str,
    event_id: str,
    description: str,
    from_timestamp: datetime,
    to_timestamp: datetime,
):
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


def get_user_events_between_timestamps(username: str, from_timestamp: datetime, to_timestamp: datetime):
    user = get_user(username)
    if user is None:
        return None
    filtered_events = [e for e in user.events if e.from_timestamp < to_timestamp and e.to_timestamp > from_timestamp]
    return filtered_events
