import asyncio
import logging
from scheduler import Scheduler
import uvicorn
from api import app
from params import db_params

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


async def run_scheduler():
    scheduler = Scheduler(db_params=db_params)
    await scheduler.start(initial_run=True)


async def run_api():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    logging.info("Запуск приложения")
    await asyncio.gather(
        run_scheduler(),
        run_api(),
        return_exceptions=True
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Программа остановлена')
    except Exception as e:
        logging.error(f'Ошибка при запуске: {e}')