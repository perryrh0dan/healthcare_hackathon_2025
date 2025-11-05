from loguru import logger

logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="1 week",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
)

logger.add(lambda msg: print(msg, end=""), level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")
