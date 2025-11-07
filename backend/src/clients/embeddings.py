from langchain_aws import BedrockEmbeddings
from dotenv import load_dotenv
from ..config import CONFIG, logger

load_dotenv()


class Embeddings:
    def __init__(self):
        try:
            self.embeddings = BedrockEmbeddings(
                model_id="amazon.titan-embed-text-v2:0",
                region_name=CONFIG["AWS_DEFAULT_REGION"],
            )
            logger.info("Using Bedrock embeddings")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
