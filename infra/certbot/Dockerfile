# Dockerfile
FROM ubuntu:22.04

EXPOSE 6000 80

# читаем переменные среды из .env
ARG APP_DOMAIN
ARG APP_DEVELOPER_EMAIL

# устанавливаем переменные среды в переменные
ENV APP_DEVELOPER_EMAIL=$APP_DEVELOPER_EMAIL
ENV APP_DOMAIN=$APP_DOMAIN

WORKDIR /certbot

COPY . /certbot/

RUN apt-get update && \
    apt-get -y install certbot && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["sh", "generate-certificate.sh"]