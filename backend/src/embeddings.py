import os
from langchain_aws import BedrockEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()


class Embeddings:
    def __init__(self):
        model = "grok"
        if model != "grok":
            self.embeddings = BedrockEmbeddings(
                model_id="amazon.titan-embed-text-v2",
                region_name=os.getenv("AWS_DEFAULT_REGION"),
            )
        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
