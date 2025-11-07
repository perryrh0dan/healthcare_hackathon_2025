from typing import Literal, Optional, TypedDict
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)

from src.clients.llm import LLM
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
    electronic_patient_record: UploadFile | None = File(None),
):
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    if electronic_patient_record is not None:
        data = await electronic_patient_record.read()

        messages = [
            {
                "role": "user",
                "content": (
                    f"""[Role]
Your are an professional doctor assistent and your job is to analyse the german electronic patient record.

[Task]
Take the Data and create a detailed report of the patient health status that can be used later on to provide details informations and guidence to the patient.

[Data]
{data}
                """
                ),
            },
        ]

        llm = LLM()
        response = llm.llm.invoke(input=messages)
        print(response)

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
        samesite="strict",  # Allow cross-origin
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user")
    return {"message": "Logged out"}


class SetupQuestionOption(TypedDict):
    label: str
    value: str


class SetupQuestion(TypedDict):
    question: str
    type: Literal["text", "number", "enum"]
    options: Optional[list[SetupQuestionOption]]
    field: str
    value: Optional[str]


@router.get("/setup")
def get_registration_questions(request: Request):
    username = request.cookies.get("user")
    if username is None:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    user = get_user(username)

    return [
        SetupQuestion(
            question="What is your first name?",
            type="text",
            field="first_name",
            options=None,
            value=user.first_name if user else None,
        ),
        SetupQuestion(
            question="What is your last name?",
            type="text",
            field="last_name",
            options=None,
            value=user.last_name if user else None,
        ),
        SetupQuestion(
            question="What is your age?",
            type="number",
            field="age",
            options=None,
            value=user.age if user else None,
        ),
        SetupQuestion(
            question="What is your height?",
            type="number",
            field="height",
            options=None,
            value=user.height if user else None,
        ),
        SetupQuestion(
            question="What is your gender?",
            type="enum",
            options=[
                SetupQuestionOption(label="Male", value="male"),
                SetupQuestionOption(label="Female", value="female"),
                SetupQuestionOption(label="Other", value="other"),
            ],
            field="gender",
            value=user.gender if user else None,
        ),
        SetupQuestion(
            question="Do you have any allergies. If so what are those?",
            type="text",
            field="allergies",
            options=None,
            value=user.allergies if user else None,
        ),
        SetupQuestion(
            question="Do you have typical health issues. If so what are those?",
            type="text",
            field="issues",
            options=None,
            value=user.issues if user else None,
        ),
        SetupQuestion(
            question="What is your goal?",
            type="text",
            field="goal",
            options=None,
            value=user.goal if user else None,
        ),
    ]
