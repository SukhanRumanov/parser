from fastapi import FastAPI, HTTPException
from db import Database, News
from pydantic import BaseModel
from typing import Optional, Any
from params import db_params

app = FastAPI(title="News Parser API")
db = Database(db_params)


class DefaultResponse(BaseModel):
    error: bool
    message: str
    payload: Optional[Any] = None


class NewsResponse(BaseModel):
    id: int
    title: str
    date: str
    text: Optional[str]
    link: str
    created_at: str


@app.get("/")
def read_root():
    return DefaultResponse(
        error=False,
        message="News Parser API is running",
        payload=None
    )


@app.get("/news/{news_id}", response_model=DefaultResponse)
def get_news_by_id(news_id: int):
    session = db.get_session()
    news = session.query(News).filter(News.id == news_id).first()
    if not news:
        DefaultResponse(error=True, message="Новостей не найдено", payload=None)

    news_data = {
        "id": news.id,
        "title": news.title,
        "date": news.date.isoformat() if news.date else "",
        "text": news.text,
        "link": news.link,
        "created_at": news.created_at.isoformat() if news.created_at else ""
    }

    return DefaultResponse(
        error=False,
        message="News found successfully",
        payload=news_data
    )
