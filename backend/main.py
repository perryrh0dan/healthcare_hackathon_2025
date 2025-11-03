import os
from dotenv import load_dotenv
import boto3
from langchain_aws import ChatBedrockConverse

load_dotenv()


def main():
    bedrock_client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_DEFAULT_REGION"))
    llm = ChatBedrockConverse(model="anthropic.claude-3-haiku", temperature=0.6, client=bedrock_client)
    response = llm.invoke("Hello?")
    print(response.content)


if __name__ == "__main__":
    main()
