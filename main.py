from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from typing import List
import json

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
    embedding: str = Field(..., description='JSON string like "[0.1, -0.2, 0.3]"')


class ContextResponse(BaseModel):
    response: List[str]


@app.post("/context", response_model=ContextResponse)
async def retrieve_context(request: EmbeddingRequest):
    try:
        embedding = json.loads(request.embedding)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="embedding must be a JSON-encoded array of numbers")

    pts = client.query_points(
        collection_name=settings.collection_name,
        query=embedding,
        limit=3,
    )
     if not isinstance(embedding, list) or len(embedding) == 0:
        raise HTTPException(status_code=400, detail="embedding must be a non-empty array")

    if any(x is None for x in embedding):
        raise HTTPException(status_code=400, detail="embedding must not contain null values")

    try:
        embedding = [float(x) for x in embedding]
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="embedding must contain only numbers")

    context = [
        point.payload.get("content", "")
        for point in pts.points
    ]

    return {"response": context}
