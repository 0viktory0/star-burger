#!/bin/bash

set -Eeuo pipefail

source venv/bin/activate

git pull

echo "building frontend"
sudo docker build -t star-burger_frontend -f dockerfiles/Dockerfile.frontend .
sudo docker run --rm -v $(pwd)/bundles:/app/bundles star-burger_frontend

echo "setting up backend"
sudo docker-compose -f docker-compose.prod.yml up -d
sudo docker exec -t django python manage.py migrate
sudo docker cp django:/app/staticfiles .

echo "Clearing unused docker items"
sudo docker system prune -f


echo "environment:" "$ROLLBAR_ENVIRONMENT"
ROLLBAR_ENVIRONMENT='production'


curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token="$DJANGO_ROLLBAR_TOKEN" \
  -F environment="$ROLLBAR_ENVIRONMENT" \
  -F revision="$REVISION" \
  -F local_username="$USERNAME"


printf "\nDeploy completed!\n"
