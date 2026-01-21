from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
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
    
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8',
   extra = 'allow')

setting = Settings()

client = QdrantClient(url = setting.url,
                      api_key = setting.api_key)

class EmbeddingRequest(BaseModel):
    embedding: List[float]


@app.post("/context/{embedding}")
async def root(embedding: EmbeddingRequest):
    pts = client.query_points(
        collection_name = setting.collection_name,
        query = embedding,
        limit = 3
    )
    context = [content.payload.get("content", "") for content in pts.points]
    return {"message": context}
