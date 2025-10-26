import logging
import threading
from scheduler import Scheduler
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_parser.log'),
        logging.StreamHandler()
    ]
)


def run_api():
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)


def run_scheduler():
    db_params = {
        'dbname': 'news_db',
        'user': 'postgres',
        'password': '123456',
        'host': 'localhost',
        'port': '5432'
    }
    scheduler = Scheduler(db_params=db_params)
    scheduler.start(initial_run=True)


def main():
    logging.info("=== NEWS PARSER SYSTEM STARTING ===")

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    logging.info("FastAPI server running on http://localhost:8000")
    logging.info("API docs: http://localhost:8000/docs")

    run_scheduler()


if __name__ == "__main__":
    main()