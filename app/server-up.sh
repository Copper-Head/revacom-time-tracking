#!/usr/bin/env bash

set -e

PORT=80
VHOST=vps441625.ovh.net

docker run -d \
    -p $PORT:80 \
    --name=nginx-proxy \
    -v /var/run/docker.sock:/tmp/docker.sock:ro \
    jwilder/nginx-proxy

docker run -d \
    --expose=$PORT \
    -e VIRTUAL_HOST=$VHOST \
    -v /home/ubuntu/bokeh/:/bokeh \
    mybokeh \
    bokeh serve --port $PORT examples/app/sliders.py --allow-websocket-origin $VHOST
