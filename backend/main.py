from src.api import app
import uvicorn
from src.config import logger


def main():
    logger.info("Starting server on host 0.0.0.0 port 8008")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8008)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    main()
