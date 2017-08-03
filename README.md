# Revacom Time Tracking


## Running

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
