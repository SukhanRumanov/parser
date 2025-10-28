import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_news(is_first_run=False):
    url = 'https://bezformata.com/'
    news_list = []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        news_sections = soup.find_all('section', class_='newtopicbox')

        now = datetime.now()
        for section in news_sections:
            news_items = section.find_all('article', class_='newtopicline')

            for item in news_items:
                try:
                    date_meta = item.find('meta', {'itemprop': 'datePublished'})
                    date_str = date_meta.get('content') if date_meta else ''
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    if is_first_run and date < now - timedelta(hours=24):
                        continue
                    link_tag = item.find('a', {'itemprop': 'url'})
                    if not link_tag:
                        continue

                    title_tag = link_tag.find('span', {'itemprop': 'name'})
                    title = title_tag.text.strip() if title_tag else ''

                    link =   link_tag.get('href')

                    data = parse_time(link)

                    full_text = parse_full_article_text(link) if link else ''

                    news_list.append({
                        'title': title,
                        'date': data,
                        'text': full_text,
                        'link': link
                    })

                except Exception as e:
                    logging.error(f"Ошибка при парсинге новости: {e}")

        logging.info(f"Спарсено {len(news_list)} новостей.")
        return news_list
    except Exception as e:
        logging.error(f"Непредвиденная ошибка в парсере: {e}")
        return []


def parse_full_article_text(article_url):
    try:
        time.sleep(0.5)
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('article')
        full_text = content_div.get_text(separator=' ', strip=True)
        full_text = ' '.join(full_text.split())
        logging.info(f"Загружен текст: {len(full_text)} символов для {article_url}")
        return full_text
    except Exception as e:
        logging.error(f"Ошибка при парсинге полной новости {article_url}: {e}")
        return ''


from datetime import datetime
import logging


def parse_time(article_url):
    try:
        response = requests.get(article_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        date_box = soup.find('div', class_='sourcedatebox')
        if not date_box:
            logging.warning(f"Не найден блок sourcedatebox для {article_url}")
            return None

        date_span = date_box.find('span', title=True)
        if not date_span:
            logging.warning(f"Не найден span с датой для {article_url}")
            return None

        date_time_text = date_span.get_text()
        date_time_text = date_time_text.replace('&nbsp;', ' ').strip()
        date_time_obj = datetime.strptime(date_time_text, '%d.%m.%Y %H:%M')

        logging.info(f"Распарсена дата: {date_time_obj} для {article_url}")
        return date_time_obj

    except Exception as e:
        logging.error(f"Ошибка при парсинге даты и времени {article_url}: {e}")
        return None

