import os
import boto3
from dotenv import load_dotenv
from .config import logger

load_dotenv()


class Healthimaging:
    def __init__(self):
        model = os.getenv("MODEL", "grok")
        try:
            if model != "grok":
                self.client = boto3.client("healthimaging", region_name=os.getenv("AWS_DEFAULT_REGION"))
                logger.info("Healthimaging client initialized")
            else:
                self.client = None
                logger.info("No Healthimaging client available")
        except Exception as e:
            logger.error(f"Failed to initialize Healthimaging client: {e}")
            raise
