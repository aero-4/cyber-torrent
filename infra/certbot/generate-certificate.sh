#!/bin/bash

rm -rf /etc/letsencrypt/live/cyber-torrent.top

certbot certonly --standalone --email dimongames6@gmail.com -d cyber-torrent.top --cert-name=certfolder --key-type rsa --agree-tos

rm -rf /etc/nginx/cert.pem
rm -rf /etc/nginx/key.pem

# копируем сертификаты из образа certbot в папку Nginx
cp /etc/letsencrypt/live/cyber-torrent.top/fullchain.pem /etc/nginx/cert.pem
cp /etc/letsencrypt/live/cyber-torrent.top/privkey.pem /etc/nginx/key.pem