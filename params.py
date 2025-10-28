import os

db_params = {
    'dbname': os.getenv('DB_NAME', 'news_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'host': os.getenv('DB_HOST', 'host.docker.internal'),
    'port': os.getenv('DB_PORT', '5432')
}