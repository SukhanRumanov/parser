from fastapi import FastAPI, HTTPException
from db import Database, News
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

app = FastAPI(title="News Parser API")
db = Database()


class NewsResponse(BaseModel):
    id: int
    title: str
    date: str
    text: Optional[str]
    link: str
    created_at: str


@app.get("/")
def read_root():
    return {"message": "News Parser API"}


@app.get("/news/{news_id}", response_model=NewsResponse)
def get_news_by_id(news_id: int):
    session = db.get_session()
    news = session.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return {
        "id": news.id,
        "title": news.title,
        "date": news.date.isoformat() if news.date else "",
        "text": news.text,
        "link": news.link,
        "created_at": news.created_at.isoformat() if news.created_at else ""
    }

