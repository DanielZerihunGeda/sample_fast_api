from typing import Optional

from fastapi import FastAPI
import aiohttp
from bs4 import BeautifulSoup

app = FastAPI()
async def fetch_text(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.get("/copilot/{query}")
async def return_ans(query: str):
    text = await fetch_text("https://ease-int.com/")
    return {"response": text}


