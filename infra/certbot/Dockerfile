FROM certbot/certbot:latest

COPY infra/certbot/entrypoint.sh /entrypoint.sh
COPY infra/certbot/copy-certs.sh /copy-certs.sh
RUN chmod +x /entrypoint.sh /copy-certs.sh

ENTRYPOINT ["/entrypoint.sh"]
