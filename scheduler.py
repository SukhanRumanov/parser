import schedule
import time
import logging
from db import Database
from pars import parse_news

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, db_params=None):
        self.db = Database(**(db_params or {}))
        self.is_running = False

    def run_parsing_job(self, is_first_run=False):
        try:
            logger.info("Запуск парсера...")
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

    def cleanup_old_news(self, days_old=1):
        try:
            logger.info(f"Запуск очистки новостей старше {days_old} дней")
            deleted_count = self.db.delete_old_news(days_old)
            logger.info(f"Очистка завершена. Удалено {deleted_count} старых новостей")
            return deleted_count
        except Exception as e:
            logger.error(f"Ошибка при очистке старых новостей: {e}")
            return 0

    def setup_schedule(self):
        schedule.every(1).hours.do(self.run_parsing_job)
        schedule.every().day.at("02:00").do(self.cleanup_old_news, days_old=1)
        logger.info("Расписание настроено: парсинг каждый час, очистка старых новостей в 02:00")

    def start(self, initial_run=True):
        if self.is_running:
            logger.warning("Планировщик уже запущен")
            return
        self.is_running = True

        if initial_run:
            logger.info("=== ПЕРВЫЙ ЗАПУСК ПАРСЕРА ===")
            self.run_parsing_job(is_first_run=True)

        self.setup_schedule()

        logger.info("Планировщик запущен. Ожидание следующих запусков по расписанию...")

        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Планировщик остановлен пользователем")
            self.stop()

    def stop(self):
        """Остановка планировщика"""
        self.is_running = False
        schedule.clear()
        logger.info("Планировщик остановлен")
