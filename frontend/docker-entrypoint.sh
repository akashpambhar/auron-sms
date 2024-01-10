#!/usr/bin/env sh
set -eu
envsubst '${API_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
envsubst '${API_URL}' < /usr/share/nginx/html/assets/config.json > /tmp/config.tmp && mv /tmp/config.tmp /usr/share/nginx/html/assets/config.json
exec "$@"
