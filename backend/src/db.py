from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid
import sqlite3
import json


class Event(BaseModel):
    id: str
    description: str
    from_timestamp: datetime
    to_timestamp: datetime


class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime
    image: Optional[str] = None


class Conversation(BaseModel):
    id: str
    messages: List[Message] = []
    state: Dict[str, Any] = {}


class Answer(BaseModel):
    question: str
    answer: str


# Database setup
conn = sqlite3.connect("healthcare.db", check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# Create tables
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    height INTEGER,
    gender TEXT,
    status TEXT NOT NULL,
    allergies TEXT,
    issues TEXT,
    goal TEXT,
    epa_summary TEXT,
    recent_summary TEXT
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    description TEXT NOT NULL,
    from_timestamp TEXT NOT NULL,
    to_timestamp TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users (username)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    state TEXT,
    FOREIGN KEY (user_id) REFERENCES users (username)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    image TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS daily_answers (
    user_id TEXT PRIMARY KEY,
    answers TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (username)
)
"""
)

conn.commit()

# Add recent_summary column if not exists
try:
    cursor.execute("ALTER TABLE users ADD COLUMN recent_summary TEXT;")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Column already exists

# Add image column to messages if not exists
try:
    cursor.execute("ALTER TABLE messages ADD COLUMN image TEXT;")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Column already exists


class User(BaseModel):
    username: str
    password: Optional[str]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    height: Optional[int] = None
    gender: Optional[Literal["male", "female", "other"]] = "other"
    status: Literal["setup", "finished"]
    allergies: Optional[str] = None
    issues: Optional[str] = None
    goal: Optional[str] = None
    epa_summary: Optional[str] = None
    recent_summary: Optional[str] = None
    needs_daily_questions: bool = False
    events: List[Event] = []


class UpdateUser(User):
    password: Optional[str] = None
    recent_summary: Optional[str] = None


def update_user(update: UpdateUser):
    user = get_user(update.username)
    if user is None:
        raise RuntimeError()

    # Use existing password if not provided
    password = update.password or user.password

    cursor.execute(
        """
    UPDATE users SET
        password = ?,
        first_name = ?,
        last_name = ?,
        age = ?,
        height = ?,
        gender = ?,
        status = ?,
        allergies = ?,
        issues = ?,
        goal = ?,
        epa_summary = ?,
        recent_summary = ?
    WHERE username = ?
    """,
        (
            password,
            update.first_name,
            update.last_name,
            update.age,
            update.height,
            update.gender,
            update.status,
            update.allergies,
            update.issues,
            update.goal,
            update.epa_summary,
            update.recent_summary,
            update.username,
        ),
    )
    conn.commit()


def create_user(user: User):
    cursor.execute(
        """
    INSERT INTO users (username, password, first_name, last_name, age, height, gender, status, allergies, issues, goal, epa_summary, recent_summary)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            user.username,
            user.password,
            user.first_name,
            user.last_name,
            user.age,
            user.height,
            user.gender,
            user.status,
            user.allergies,
            user.issues,
            user.goal,
            user.epa_summary,
            user.recent_summary,
        ),
    )
    conn.commit()


def get_user(username: str):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row:
        user = User(
            username=row[0],
            password=row[1],
            first_name=row[2],
            last_name=row[3],
            age=row[4],
            height=row[5],
            gender=row[6],
            status=row[7],
            allergies=row[8],
            issues=row[9],
            goal=row[10],
            epa_summary=row[11],
            recent_summary=row[12],
            events=get_user_events(username) or [],
        )

        today = datetime.now().date().isoformat()
        daily_answers = get_daily_answers(username)
        user.needs_daily_questions = not any(
            entry["date"].startswith(today) for entry in daily_answers
        )
        return user
    return None


def add_event(
    username: str, description: str, from_timestamp: datetime, to_timestamp: datetime
):
    user = get_user(username)
    if user is None:
        return None
    event_id = str(uuid.uuid4())
    cursor.execute(
        """
    INSERT INTO events (id, username, description, from_timestamp, to_timestamp)
    VALUES (?, ?, ?, ?, ?)
    """,
        (
            event_id,
            username,
            description,
            from_timestamp.isoformat(),
            to_timestamp.isoformat(),
        ),
    )
    conn.commit()
    return Event(
        id=event_id,
        description=description,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
    )


def remove_event(username: str, event_id: str):
    cursor.execute(
        "DELETE FROM events WHERE id = ? AND username = ?", (event_id, username)
    )
    conn.commit()
    return cursor.rowcount > 0


def edit_event(
    username: str,
    event_id: str,
    description: str,
    from_timestamp: datetime,
    to_timestamp: datetime,
):
    cursor.execute(
        """
    UPDATE events SET description = ?, from_timestamp = ?, to_timestamp = ?
    WHERE id = ? AND username = ?
    """,
        (
            description,
            from_timestamp.isoformat(),
            to_timestamp.isoformat(),
            event_id,
            username,
        ),
    )
    conn.commit()
    return cursor.rowcount > 0


def get_user_events(username: str):
    cursor.execute(
        "SELECT id, description, from_timestamp, to_timestamp FROM events WHERE username = ?",
        (username,),
    )
    rows = cursor.fetchall()
    events = []
    for row in rows:
        events.append(
            Event(
                id=row[0],
                description=row[1],
                from_timestamp=datetime.fromisoformat(row[2]),
                to_timestamp=datetime.fromisoformat(row[3]),
            )
        )
    return events


def get_user_events_between_timestamps(
    username: str, from_timestamp: datetime, to_timestamp: datetime
):
    cursor.execute(
        """
    SELECT id, description, from_timestamp, to_timestamp FROM events
    WHERE username = ? AND from_timestamp < ? AND to_timestamp > ?
    """,
        (username, to_timestamp.isoformat(), from_timestamp.isoformat()),
    )
    rows = cursor.fetchall()
    events = []
    for row in rows:
        events.append(
            Event(
                id=row[0],
                description=row[1],
                from_timestamp=datetime.fromisoformat(row[2]),
                to_timestamp=datetime.fromisoformat(row[3]),
            )
        )
    return events


def create_conversation(user_id: str, conversation_id: str):
    cursor.execute(
        "INSERT INTO conversations (id, user_id, state) VALUES (?, ?, ?)",
        (conversation_id, user_id, json.dumps({})),
    )
    conn.commit()


def get_conversation(user_id: str, conversation_id: str) -> Optional[Conversation]:
    cursor.execute(
        "SELECT state FROM conversations WHERE id = ? AND user_id = ?",
        (conversation_id, user_id),
    )
    row = cursor.fetchone()
    if not row:
        return None
    state = json.loads(row[0])
    # Get messages
    cursor.execute(
        "SELECT role, content, timestamp, image FROM messages WHERE conversation_id = ? ORDER BY timestamp",
        (conversation_id,),
    )
    message_rows = cursor.fetchall()
    messages = []
    for msg_row in message_rows:
        messages.append(
            Message(
                role=msg_row[0],
                content=msg_row[1],
                timestamp=datetime.fromisoformat(msg_row[2]),
                image=msg_row[3],
            )
        )
    return Conversation(id=conversation_id, messages=messages, state=state)


def update_conversation(
    user_id: str, conversation_id: str, messages: List[Message], state: Dict[str, Any]
):
    # Update state
    cursor.execute(
        "UPDATE conversations SET state = ? WHERE id = ? AND user_id = ?",
        (json.dumps(state), conversation_id, user_id),
    )
    # Delete existing messages
    cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    # Insert new messages
    for message in messages:
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content, timestamp, image) VALUES (?, ?, ?, ?, ?)",
            (
                conversation_id,
                message.role,
                message.content,
                message.timestamp.isoformat(),
                message.image,
            ),
        )
    conn.commit()


def get_user_conversations(user_id: str) -> Dict[str, Conversation]:
    cursor.execute("SELECT id FROM conversations WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conversations = {}
    for row in rows:
        conv = get_conversation(user_id, row[0])
        if conv:
            conversations[row[0]] = conv
    return conversations


def save_daily_answers(user_id: str, answers: List[Answer]):
    current_answers = get_daily_answers(user_id)
    new_entry = {"date": datetime.now().isoformat(), "answers": answers}
    current_answers.append(new_entry)
    cursor.execute(
        "INSERT OR REPLACE INTO daily_answers (user_id, answers) VALUES (?, ?)",
        (user_id, json.dumps(current_answers)),
    )
    conn.commit()


def get_daily_answers(user_id: str) -> List[Dict[str, Any]]:
    cursor.execute("SELECT answers FROM daily_answers WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        loaded = json.loads(row[0])
        if (
            isinstance(loaded, list)
            and loaded
            and isinstance(loaded[0], dict)
            and "date" in loaded[0]
        ):
            return loaded
        else:
            # Old format, wrap it
            return [{"date": None, "answers": loaded}]
    return []


def update_recent_summary(username: str, summary: str):
    cursor.execute(
        "UPDATE users SET recent_summary = ? WHERE username = ?",
        (summary, username),
    )
    conn.commit()


def get_recent_summary(username: str) -> Optional[str]:
    cursor.execute("SELECT recent_summary FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return None
