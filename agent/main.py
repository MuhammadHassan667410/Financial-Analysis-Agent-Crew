import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv(override=True)

azure_llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
)
print(f"✅ Successfully initialized LLM: {azure_llm}")