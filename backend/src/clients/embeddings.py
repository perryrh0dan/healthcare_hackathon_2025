from langchain_aws import BedrockEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
from ..config import CONFIG, logger

load_dotenv()


class Embeddings:
    def __init__(self):
        model = CONFIG["MODEL"]
        try:
            if model != "grok":
                self.embeddings = BedrockEmbeddings(
                    model_id="amazon.titan-embed-text-v2",
                    region_name=CONFIG["AWS_DEFAULT_REGION"],
                )
                logger.info("Using Bedrock embeddings")
            else:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},
                )
                logger.info("Using HuggingFace embeddings")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
