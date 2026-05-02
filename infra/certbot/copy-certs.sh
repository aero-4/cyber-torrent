#!/bin/sh
set -eu

: "${DOMAIN:?DOMAIN is required}"

SRC="/etc/letsencrypt/live/${DOMAIN}"
DST="/nginx-certs/${DOMAIN}"

if [ ! -f "${SRC}/fullchain.pem" ] || [ ! -f "${SRC}/privkey.pem" ]; then
  echo "Certificate files not found in ${SRC}" >&2
  exit 1
fi

mkdir -p "${DST}"
install -m 0644 -D "${SRC}/fullchain.pem" "${DST}/fullchain.pem"
install -m 0600 -D "${SRC}/privkey.pem" "${DST}/privkey.pem"
