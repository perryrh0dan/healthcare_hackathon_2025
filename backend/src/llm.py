import os
import boto3
from langchain_aws import ChatBedrockConverse
from langchain_xai import ChatXAI
from dotenv import load_dotenv

load_dotenv()


class LLM:
    def __init__(self):
        model = "grok"
        if model != "grok":
            self.bedrock_client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_DEFAULT_REGION"))

            self.llm = ChatBedrockConverse(model="anthropic.claude-3-haiku", temperature=0.6, client=self.bedrock_client)
        else:
            self.llm = ChatXAI(model="grok-4-fast")
