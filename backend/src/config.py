import os
from loguru import logger

CONFIG = {
    "MODEL": os.getenv("MODEL", "grok"),
    "AWS_DEFAULT_REGION": os.getenv("AWS_DEFAULT_REGION", "us-west-2"),
}

logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="1 week",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
)

logger.add(lambda msg: print(msg, end=""), level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
