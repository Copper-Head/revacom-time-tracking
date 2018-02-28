#!/usr/bin/env bash
set -e

curl -fsSL get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo curl -L https://github.com/docker/compose/releases/download/1.19.0/docker-compose-`uname -s`-`uname -m` \
          -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

bash scraper.sh

docker-compose up -d
