from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
import psycopg2
from datetime import timedelta

logger = logging.getLogger(__name__)

Base = declarative_base()


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    text = Column(Text)
    link = Column(Text, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class Database:
    def __init__(self, db_params):
        dbname = db_params['dbname']
        user = db_params['user']
        password = db_params['password']
        host = db_params['host']
        port = db_params['port']

        self.engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
        self.Session = sessionmaker(bind=self.engine)
        try:
            with self.engine.connect():
                logger.info(f"Успешное подключение к базе данных {dbname}")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def link_exists(self, link):
        session = self.get_session()
        try:
            return session.query(News).filter(News.link == link).first() is not None
        finally:
            session.close()

    def insert_news(self, news_list):
        if not news_list:
            return 0

        session = self.get_session()
        try:
            for news_item in news_list:
                news = News(
                    title=news_item['title'],
                    date=news_item['date'],
                    text=news_item['text'],
                    link=news_item['link']
                )
                session.add(news)
            session.commit()
            return len(news_list)
        except:
            session.rollback()
            return 0
        finally:
            session.close()

    def get_news_count(self):
        session = self.get_session()
        try:
            return session.query(News).count()
        finally:
            session.close()

    def get_news_by_id(self, news_id):
        session = self.get_session()
        try:
            return session.query(News).filter(News.id == news_id).first()
        finally:
            session.close()