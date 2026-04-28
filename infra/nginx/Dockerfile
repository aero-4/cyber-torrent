FROM nginx:alpine
RUN apk add --no-cache gettext

WORKDIR /usr/share/nginx/html

COPY infra/nginx/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
