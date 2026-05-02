FROM certbot/certbot:latest

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash coreutils \
    && rm -rf /var/lib/apt/lists/*

COPY infra/certbot/entrypoint.sh /entrypoint.sh
COPY infra/certbot/copy-certs.sh /copy-certs.sh
RUN chmod +x /entrypoint.sh /copy-certs.sh

ENTRYPOINT ["/entrypoint.sh"]
