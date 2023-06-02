#!/bin/bash

set -Eeuo pipefail

source venv/bin/activate

git pull

pip install -r requirements.txt
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --publ>
python manage.py collectstatic --noinput
python manage.py migrate --noinput
systemctl daemon-reload
systemctl reload django.service
systemctl reload nginx.service

USERNAME=$(whoami)
REVISION='1.0'
DJANGO_ROLLBAR_TOKEN='7d6ea264d7eb401286964807e74089c7'
ROLLBAR_ENVIRONMENT='production'


curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token="$DJANGO_ROLLBAR_TOKEN" \
  -F environment="$ROLLBAR_ENVIRONMENT" \
  -F revision="$REVISION" \
  -F local_username="$USERNAME"


printf "\nDeploy completed!\n"
