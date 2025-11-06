from typing import TypedDict
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.exceptions import FastAPIError
from loguru import logger
from http import HTTPStatus

from src.db import User, create_user, get_user


class RegisterUserDTO(TypedDict):
    username: str
    password: str


class LoginDTO(TypedDict):
    username: str
    password: str


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def me(request: Request):
    logger.debug("me")
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    return get_user(username)


@router.post("/register")
async def register(data: RegisterUserDTO):
    create_user(
        User(
            username=data["username"],
            password=data["password"],
            status="setup",
        )
    )


@router.post("/login")
async def login(data: LoginDTO, response: Response):
    user = get_user(data["username"])
    if user is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST)

    response.set_cookie(
        key="user",
        value=data["username"],
        max_age=3600,  # seconds
        httponly=True,  # cannot access from JS
        secure=False,  # True if using HTTPS
        samesite="none",  # Allow cross-origin
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user")
    return {"message": "Logged out"}
