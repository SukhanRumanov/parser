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

                    full_text = parse_full_article_text(link) if link else ''

                    news_list.append({
                        'title': title,
                        'date': date,
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
        paragraphs = content_div.find_all('p')
        if paragraphs == []:
            paragraphs = content_div.find_all('a')
        meaningful_paragraphs = []
        for paragraph in paragraphs:
            text = paragraph.get_text(strip=True)
            meaningful_paragraphs.append(text)
        full_text = ' '.join(meaningful_paragraphs)
        logging.info(f"Загружен текст: {len(full_text)} символов для {article_url}")
        return full_text
    except Exception as e:
        logging.error(f"Ошибка при парсинге полной новости {article_url}: {e}")
        return ''