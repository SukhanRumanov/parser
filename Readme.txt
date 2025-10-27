 docker build -t news-parser .
 docker run -p 8000:8000 --add-host=host.docker.internal:host-gateway news-parser

