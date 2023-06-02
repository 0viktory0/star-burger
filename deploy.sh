#!/bin/bash

set -Eeuo pipefail

source venv/bin/activate

git pull

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
systemctl reload django.service
systemctl reload nginx.service

USERNAME=$(whoami)
REVISION='1.0'
echo "environment:" "$ROLLBAR_ENVIRONMENT"
ROLLBAR_ENVIRONMENT='production'


curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token="$DJANGO_ROLLBAR_TOKEN" \
  -F environment="$ROLLBAR_ENVIRONMENT" \
  -F revision="$REVISION" \
  -F local_username="$USERNAME"


printf "\nDeploy completed!\n"
