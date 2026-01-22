from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from qdrant_client import QdrantClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware( 
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

class Settings(BaseSettings):
    url: str
    api_key: str
    collection_name: str
    google_api_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

settings = Settings()

client = QdrantClient(url=settings.url, api_key=settings.api_key)

embedding_model = GoogleGenerativeAIEmbeddings(
    google_api_key=settings.google_api_key,
    model="gemini-embedding-001"
)

class EmbeddingRequest(BaseModel):
    query: str = Field(..., description="Query string for similarity search")

class ContextResponse(BaseModel):
    response: List[str]

@app.post("/context", response_model=ContextResponse)
async def retrieve_context(req: EmbeddingRequest):
    embedding = embedding_model.embed_query(req.query)

    pts = client.query_points(
        collection_name=settings.collection_name,
        query=embedding,
        limit=3,
    )

    context = [point.payload.get("content", "") for point in pts.points]
    return {"response": context}
