from typing import TypedDict
from fastapi import APIRouter
from loguru import logger

from src.db import User, create_user, get_user


class UserDTO(TypedDict):
    first_name: str
    last_name: str
    age: int


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def me():
    logger.debug("me")
    get_user("test")


async def register(user: UserDTO):
    create_user(
        User(
            first_name=user["first_name"],
            last_name=user["last_name"],
            age=user["age"],
            status="setup",
        )
    )
