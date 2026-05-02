FROM nginx:stable-alpine

RUN apk add --no-cache bash openssl inotify-tools gettext

COPY infra/nginx/nginx.conf.template /etc/nginx/nginx.conf.template
COPY infra/nginx/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]
