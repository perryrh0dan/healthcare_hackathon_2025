import boto3
from langchain_aws import ChatBedrockConverse
from langchain_xai import ChatXAI
from dotenv import load_dotenv
from ..config import CONFIG, logger

load_dotenv()


class LLM:
    def __init__(self):
        try:
            self.bedrock_client = boto3.client("bedrock-runtime", region_name=CONFIG["AWS_DEFAULT_REGION"])
            self.llm = ChatBedrockConverse(
                model="anthropic.claude-sonnet-4-5-20250929-v1:0",
                temperature=0.6,
                client=self.bedrock_client,
            )
            logger.info("Using Bedrock LLM")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
