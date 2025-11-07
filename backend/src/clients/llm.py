import boto3
from langchain_aws import ChatBedrockConverse
from langchain_xai import ChatXAI
from dotenv import load_dotenv
from ..config import CONFIG, logger

load_dotenv()


class LLM:
    def __init__(self):
        model = CONFIG["MODEL"]
        try:
            if model != "grok":
                self.bedrock_client = boto3.client("bedrock-runtime", region_name=CONFIG["AWS_DEFAULT_REGION"])
                self.llm = ChatBedrockConverse(
                    model="anthropic.claude-3-haiku",
                    temperature=0.6,
                    client=self.bedrock_client,
                )
                logger.info("Using Bedrock LLM")
            else:
                self.llm = ChatXAI(model="grok-4-fast")
                logger.info("Using XAI LLM")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
