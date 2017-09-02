FROM continuumio/miniconda3

RUN conda config --set always_yes True && \
    conda config --system --append channels conda-forge && \
    conda config --set auto_update_conda False

RUN conda install --quiet \
    beautifulsoup4=4.6.* \
    requests=2.14.* && \
    conda clean -tipsy

VOLUME /data
VOLUME /secrets

ADD scraper.py scraper.py

CMD ["python", "scraper.py"]
