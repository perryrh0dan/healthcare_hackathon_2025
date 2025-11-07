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
    title: Optional[str] = None


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
    username TEXT NOT NULL,
    state TEXT,
    FOREIGN KEY (username) REFERENCES users (username)
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
    username TEXT,
    answers TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users (username)
    PRIMARY KEY (username, date)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS daily_questions (
    username TEXT NOT NULL,
    date TEXT NOT NULL,
    questions TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users (username),
    PRIMARY KEY (username, date)
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS daily_dashboard_widgets (
    username TEXT NOT NULL,
    date TEXT NOT NULL,
    widgets TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users (username),
    PRIMARY KEY (username, date)
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

# Add title column to conversations if not exists
try:
    cursor.execute("ALTER TABLE conversations ADD COLUMN title TEXT;")
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


def create_conversation(username: str, conversation_id: str):
    cursor.execute(
        "INSERT INTO conversations (id, username, state, title) VALUES (?, ?, ?, ?)",
        (conversation_id, username, json.dumps({}), None),
    )
    conn.commit()


def get_conversation(username: str, conversation_id: str) -> Optional[Conversation]:
    cursor.execute(
        "SELECT state, title FROM conversations WHERE id = ? AND username = ?",
        (conversation_id, username),
    )
    row = cursor.fetchone()
    if not row:
        return None
    state = json.loads(row[0])
    title = row[1]
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
    return Conversation(id=conversation_id, messages=messages, state=state, title=title)


def update_conversation(
    username: str,
    conversation_id: str,
    messages: List[Message],
    state: Dict[str, Any],
    title: Optional[str] = None,
):
    # Update state and title
    cursor.execute(
        "UPDATE conversations SET state = ?, title = ? WHERE id = ? AND username = ?",
        (json.dumps(state), title, conversation_id, username),
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


def get_user_conversations(username: str) -> Dict[str, Conversation]:
    cursor.execute("SELECT id FROM conversations WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conversations = {}
    for row in rows:
        conv = get_conversation(username, row[0])
        if conv:
            conversations[row[0]] = conv
    return conversations


def save_daily_answers(username: str, answers: List[Answer]):
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO daily_answers (username, date, answers) VALUES (?, ?, ?)",
        (username, now, json.dumps(answers)),
    )
    conn.commit()


def get_daily_answers(username: str) -> List[Dict[str, Any]]:
    cursor.execute("SELECT answers FROM daily_answers WHERE username = ?", (username,))
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


def save_daily_questions(username: str, questions: List[Dict[str, Any]]):
    today = datetime.now().date().isoformat()
    cursor.execute(
        "INSERT OR REPLACE INTO daily_questions (username, date, questions) VALUES (?, ?, ?)",
        (username, today, json.dumps(questions)),
    )
    conn.commit()


def get_daily_questions(username: str) -> Optional[List[Dict[str, Any]]]:
    today = datetime.now().date().isoformat()
    cursor.execute(
        "SELECT questions FROM daily_questions WHERE username = ? AND date = ?",
        (username, today),
    )
    row = cursor.fetchone()
    if row:
        return json.loads(row[0])
    return None


def save_daily_dashboard_widgets(username: str, widgets: List[Dict[str, Any]]):
    today = datetime.now().date().isoformat()
    cursor.execute(
        "INSERT OR REPLACE INTO daily_dashboard_widgets (username, date, widgets) VALUES (?, ?, ?)",
        (username, today, json.dumps(widgets)),
    )
    conn.commit()


def get_daily_dashboard_widgets(username: str) -> Optional[List[Dict[str, Any]]]:
    today = datetime.now().date().isoformat()
    cursor.execute(
        "SELECT widgets FROM daily_dashboard_widgets WHERE username = ? AND date = ?",
        (username, today),
    )
    row = cursor.fetchone()
    if row:
        return json.loads(row[0])
    return None


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


def get_all_users() -> List[str]:
    cursor.execute("SELECT username FROM users")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


def generate_daily_questions_for_all_users():
    from .utils import get_recent_messages
    from .state import questions_graph

    users = get_all_users()
    for username in users:
        user = get_user(username)
        if user is None:
            continue

        base_questions = [
            {
                "question": "How are you?",
                "type": "enum",
                "options": [
                    {"value": "verygood", "label": "Very good"},
                    {"value": "good", "label": "Good"},
                    {"value": "okay", "label": "Okay"},
                    {"value": "notgood", "label": "Not good"},
                    {"value": "bad", "label": "Bad"},
                ],
                "optional": False,
            },
            {
                "question": "What is your blood pressure?",
                "type": "text",
                "options": None,
                "optional": False,
            },
            {
                "question": "What is your weight?",
                "type": "number",
                "options": None,
                "optional": False,
            },
            {
                "question": "Did you take any medication today?",
                "type": "enum",
                "options": [
                    {"value": "yes", "label": "Yes"},
                    {"value": "no", "label": "No"},
                ],
                "optional": False,
            },
        ]

        recent_messages = get_recent_messages(username)
        additional_questions = questions_graph.chat(
            recent_messages, base_questions, user
        )
        additional_questions = additional_questions[:2]
        all_questions = base_questions + additional_questions

        save_daily_questions(username, all_questions)


def generate_daily_dashboard_for_all_users():
    from .clients.llm import LLM
    from .graphs.dashboardgraph import DashboardGraph

    users = get_all_users()
    llm = LLM()
    graph = DashboardGraph(llm.llm)

    for username in users:
        user = get_user(username)
        if user is None:
            continue

        widgets = graph.run(user.__dict__)
        save_daily_dashboard_widgets(username, [widget.__dict__ for widget in widgets])
