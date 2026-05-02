#!/bin/sh
set -eu

: "${DOMAIN:?DOMAIN is required}"

ACTIVE_CERT_DIR="/etc/nginx/certs/${DOMAIN}"
mkdir -p "${ACTIVE_CERT_DIR}"

if [ ! -s "${ACTIVE_CERT_DIR}/fullchain.pem" ] || [ ! -s "${ACTIVE_CERT_DIR}/privkey.pem" ]; then
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout "${ACTIVE_CERT_DIR}/privkey.pem" \
    -out "${ACTIVE_CERT_DIR}/fullchain.pem" \
    -subj "/CN=${DOMAIN}"
fi

envsubst '${DOMAIN}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

(
  inotifywait -m -r -e close_write,move,create,delete "${ACTIVE_CERT_DIR}" 2>/dev/null |
  while read -r _; do
    nginx -s reload || true
  done
) &

exec nginx -g 'daemon off;'
