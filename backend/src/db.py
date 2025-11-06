from typing import Literal, Optional
from pydantic import BaseModel

users = []


class User(BaseModel):
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    status: Literal["setup", "finished"]


def create_user(user: User):
    users.append(user)


def get_user(username: str):
    for user in users:
        if user.username == username:
            return user
    return None
