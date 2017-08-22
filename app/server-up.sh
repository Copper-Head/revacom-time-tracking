#!/usr/bin/env bash

PORT=80

docker run -d \
    -p $PORT:80 \
    --name=nginx-proxy \
    -v
    jwilder/nginx-proxy

docker run -d \
    --expose=$PORT \
    -e VIRTUAL_HOST=vps441625.ovh.net \
    -v $HOME/bokeh/:/bokeh \
    mybokeh \
    bokeh serve --port $PORT examples/app/sliders.py
