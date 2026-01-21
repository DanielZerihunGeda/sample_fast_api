from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from qdrant_client import QdrantClient
from typing import List


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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

settings = Settings()

client = QdrantClient(
    url=settings.url,
    api_key=settings.api_key
)

class EmbeddingRequest(BaseModel):
    embedding: List[float]

class ContextResponse(BaseModel):
    response: List[str]


@app.post("/context", response_model=ContextResponse)
async def retrieve_context(request: EmbeddingRequest):
    pts = client.query_points(
        collection_name=settings.collection_name,
        query=request.embedding,
        limit=3,
    )

    context = [
        point.payload.get("content", "")
        for point in pts.points
    ]

    return {"response": context}
