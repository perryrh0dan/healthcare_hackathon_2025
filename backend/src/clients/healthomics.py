import boto3
from dotenv import load_dotenv
from ..config import CONFIG, logger

load_dotenv()


class Healthomics:
    def __init__(self):
        model = CONFIG["MODEL"]
        try:
            if model != "grok":
                self.client = boto3.client("omics", region_name=CONFIG["AWS_DEFAULT_REGION"])
                logger.info("Healthomics client initialized")
            else:
                self.client = None
                logger.info("No Healthomics client available")
        except Exception as e:
            logger.error(f"Failed to initialize Healthomics client: {e}")
            raise
