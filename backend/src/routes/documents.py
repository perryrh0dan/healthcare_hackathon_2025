from fastapi import APIRouter, File, UploadFile
from ..config import logger

from ..clients.llm import LLM

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/epa/")
async def get_daily_questions(file: UploadFile = File(...)):
    logger.debug("Received ePA")
    filename = file.filename

    contents = await file.read()

    messages = [
        {
            "role": "user",
            "content": (
                f"""[Role]
Your are an professional doctor assistent and your job is to analyse the german electronic patient record.

[Task]
Take the Data and create a detailed report of the patient health status that can be used later on to provide details informations and guidence to the patient.

[Data]
{contents}
            """
            ),
        },
    ]

    llm = LLM()
    response = llm.llm.invoke(input=messages)
    print(response)
