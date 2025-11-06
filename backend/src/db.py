from typing import Literal
from pydantic import BaseModel

users = []


class User(BaseModel):
    first_name: str
    last_name: str
    age: int
    status: Literal["setup", "finished"]


def create_user(user: User):
    users.append(user)


def get_user(user_id: str):
    users[0]
