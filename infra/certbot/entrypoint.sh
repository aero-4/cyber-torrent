#!/bin/sh
set -eu

: "${DOMAIN:?DOMAIN is required}"
: "${LETSENCRYPT_EMAIL:?LETSENCRYPT_EMAIL is required}"

CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"

if [ ! -f "${CERT_DIR}/fullchain.pem" ]; then
  certbot certonly \
    --webroot -w /var/www/certbot \
    -d "${DOMAIN}" \
    --email "${LETSENCRYPT_EMAIL}" \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    --keep-until-expiring \
    --deploy-hook /copy-certs.sh
fi

/copy-certs.sh || true

while :; do
  certbot renew \
    --webroot -w /var/www/certbot \
    --deploy-hook /copy-certs.sh
  sleep 12h
done
