# Revacom Time Tracking


## Bokeh Server

Build the container first:
```
docker build -t tt-bokeh -f app/Dockerfile .
```

And run it:
```
docker run -d -p 80:80 -v /srv/data:/data --name tt-bokeh tt-bokeh --port 80 --allow-websocket-origin=vps441625.ovh.net
```

## Running Scraper Job

Trying to support both dockerized and non-dockerized setups proved to be trickier than expected,
so for now this only runs in a docker container.

```
docker build . -t time-tracking-scraper
```

When you run the container you need to mount two volumes:

- one in `/project` containing `TimeSheetData.ipynb` and `scraper.py` (the easiest is to just mount this repository)
- one under `/data/` where the output will be saved

Here's an example run command assuming there is a `/data` directory on the host.
```
docker run -v /data:/data/ /project:$PWD time-tracking-scraper
```
