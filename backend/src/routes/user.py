from typing import Literal, TypedDict
from fastapi import APIRouter, Form, HTTPException, Request, Response, status
from fastapi.exceptions import FastAPIError
from ..config import logger
from http import HTTPStatus

from src.db import UpdateUser, User, create_user, get_user, update_user


class RegisterUserDTO(TypedDict):
    username: str
    password: str


class LoginDTO(TypedDict):
    username: str
    password: str


class SetupDTO(TypedDict):
    first_name: str
    last_name: str
    age: int
    height: int
    gender: Literal["male", "female", "other"]
    allergies: str
    issues: str
    goal: str


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


@router.post("/setup")
async def setup(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    age: int = Form(...),
    height: int = Form(...),
    gender: Literal["male", "female", "other"] = Form(...),
    allergies: str = Form(...),
    issues: str = Form(...),
    goal: str = Form(...),
):
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    update_user(
        UpdateUser(
            username=username,
            first_name=first_name,
            last_name=last_name,
            age=age,
            height=height,
            gender=gender,
            allergies=allergies,
            issues=issues,
            goal=goal,
            status="finished",
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
