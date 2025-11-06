import os
import boto3
from dotenv import load_dotenv
from ..config import logger

load_dotenv()


class Healthlake:
    def __init__(self):
        model = os.getenv("MODEL", "grok")
        try:
            if model != "grok":
                self.client = boto3.client("healthlake", region_name=os.getenv("AWS_DEFAULT_REGION"))
                logger.info("Healthlake client initialized")
            else:
                self.client = None
                logger.info("No healthlake client available")
        except Exception as e:
            logger.error(f"Failed to initialize healthlake client: {e}")
            raise
