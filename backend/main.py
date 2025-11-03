from dotenv import load_dotenv
from src.api import app
import uvicorn

load_dotenv()


def main():
    uvicorn.run(app, host="0.0.0.0", port=8008)


if __name__ == "__main__":
    main()
