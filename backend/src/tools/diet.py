from langchain.tools import tool
import json
from datetime import datetime, timedelta
from ..config import logger
from .calendar import add_calendar_event, get_calendar_events_between_timestamps, edit_calendar_event, remove_calendar_event


@tool()
def add_meal_to_calendar(username: str, meal_type: str, description: str, date: str, time: str):
    """Add a meal to the user's calendar. meal_type: breakfast, lunch, dinner, snack. date: YYYY-MM-DD, time: HH:MM"""
    logger.debug(f"Adding meal for user: {username}")
    try:
        from_dt = datetime.fromisoformat(f"{date}T{time}")
        to_dt = from_dt + timedelta(minutes=30)  # assume 30 min meal
        full_desc = f"Diet - {meal_type.capitalize()}: {description}"
        result = add_calendar_event.run({
            "username": username,
            "description": full_desc,
            "from_timestamp": from_dt.isoformat(),
            "to_timestamp": to_dt.isoformat()
        })
        logger.info(f"Added meal for user: {username}")
        return result
    except Exception as e:
        logger.error(f"Error adding meal for user {username}: {e}")
        return f"Error adding meal: {str(e)}"


@tool()
def get_meals_for_day(username: str, date: str):
    """Get diet meals for a specific day. date: YYYY-MM-DD"""
    logger.debug(f"Getting meals for user: {username} on {date}")
    try:
        start = datetime.fromisoformat(f"{date}T00:00")
        end = start + timedelta(days=1)
        events = get_calendar_events_between_timestamps.run({
            "username": username,
            "from_timestamp": start.isoformat(),
            "to_timestamp": end.isoformat()
        })
        data = json.loads(events)
        diet_events = [e for e in data["events"] if e["description"].startswith("Diet - ")]
        logger.info(f"Retrieved {len(diet_events)} meals for user: {username}")
        return json.dumps({"username": username, "meals": diet_events})
    except Exception as e:
        logger.error(f"Error getting meals for user {username}: {e}")
        return f"Error getting meals: {str(e)}"


@tool()
def edit_meal(username: str, event_id: str, meal_type: str, description: str, date: str, time: str):
    """Edit a diet meal. meal_type: breakfast, lunch, dinner, snack. date: YYYY-MM-DD, time: HH:MM"""
    logger.debug(f"Editing meal {event_id} for user: {username}")
    try:
        from_dt = datetime.fromisoformat(f"{date}T{time}")
        to_dt = from_dt + timedelta(minutes=30)
        full_desc = f"Diet - {meal_type.capitalize()}: {description}"
        result = edit_calendar_event.run({
            "username": username,
            "event_id": event_id,
            "description": full_desc,
            "from_timestamp": from_dt.isoformat(),
            "to_timestamp": to_dt.isoformat()
        })
        logger.info(f"Edited meal {event_id} for user: {username}")
        return result
    except Exception as e:
        logger.error(f"Error editing meal {event_id} for user {username}: {e}")
        return f"Error editing meal: {str(e)}"


@tool()
def remove_meal(username: str, event_id: str):
    """Remove a diet meal."""
    logger.debug(f"Removing meal {event_id} for user: {username}")
    try:
        result = remove_calendar_event.run({"username": username, "event_id": event_id})
        logger.info(f"Removed meal {event_id} for user: {username}")
        return result
    except Exception as e:
        logger.error(f"Error removing meal {event_id} for user {username}: {e}")
        return f"Error removing meal: {str(e)}"