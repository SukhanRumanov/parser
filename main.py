import asyncio
import logging
from scheduler import Scheduler
import uvicorn
from api import app
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def run_scheduler():
    db_params = {
        'dbname': 'news_db',
        'user': 'postgres',
        'password': '123456',
        'host': 'localhost',
        'port': '5432'
    }
    scheduler = Scheduler(db_params=db_params)
    await scheduler.start(initial_run=True)


async def main():
    logging.info("Запуск")
    task = asyncio.create_task(run_scheduler())
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config)
    try:
        await server.serve()
    finally:
        task.cancel()
        logging.info("Планировщик остановлен")


if __name__ == "__main__":
    asyncio.run(main())