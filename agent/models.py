import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings


from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

folder_path = "/pdf"

model = ChatOpenAI(
    api_key=os.getenv("LANGUAGE_MODEL_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LANGUAGE_MODEL"),
)

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
