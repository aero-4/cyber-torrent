#!/bin/bash

rm -rf /etc/letsencrypt/live/cyber-torrent.top

certbot certonly --standalone --email dimongames6@gmail.com -d potok.cloud --cert-name=certfolder --key-type rsa --agree-tos

rm -rf /etc/nginx/cert.pem
rm -rf /etc/nginx/key.pem

cp /etc/letsencrypt/live/potok.cloud/fullchain.pem /etc/nginx/cert.pem
cp /etc/letsencrypt/live/potok.cloud/privkey.pem /etc/nginx/key.pem