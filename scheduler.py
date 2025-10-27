import asyncio
import logging
from db import Database
from pars import parse_news
import schedule

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, db_params=None):
        self.db = Database(**(db_params or {}))
        self.is_running = False

    async def run_pars(self, is_first_run=False):
        try:
            news = parse_news(is_first_run=is_first_run)
            if not is_first_run:
                filtered_news = [item for item in news if not self.db.link_exists(item['link'])]
            else:
                filtered_news = news

            if filtered_news:
                inserted_count = self.db.insert_news(filtered_news)
                logger.info(f"Парсинг завершен. Найдено {len(news)} новостей, добавлено {inserted_count} новых")
                total_count = self.db.get_news_count()
                logger.info(f"Всего новостей в базе: {total_count}")
            else:
                logger.info("Новых новостей не найдено")

        except Exception as e:
            logger.error(f"Ошибка при выполнении задачи парсинга: {e}")

    async def delet_old(self, days_old=1):
        try:
            logger.info(f"Запуск очистки новостей старше {days_old} дней")
            deleted_count = self.db.delete_old_news(days_old)
            logger.info(f"Очистка завершена. Удалено {deleted_count} старых новостей")
            return deleted_count
        except Exception as e:
            logger.error(f"Ошибка при очистке старых новостей: {e}")
            return 0

    def setup_schedule(self):
        schedule.every(1).hours.do(self.run_pars)
        schedule.every().day.at("00:00").do(self.delet_old, 1)
        logger.info("Обновление парсера каждый день в 00.00")

    async def start(self, initial_run=True):
        if self.is_running:
            return
        self.is_running = True

        if initial_run:
            logger.info("Запуск парсера")
            await self.run_pars(is_first_run=True)

        self.setup_schedule()
        while self.is_running:
            await schedule.run_pending()
            await asyncio.sleep(60)

