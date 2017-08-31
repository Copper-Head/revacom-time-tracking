FROM continuumio/miniconda3

RUN conda config --set always_yes True && \
    conda config --system --append channels conda-forge && \
    conda config --set auto_update_conda False

RUN conda install --quiet \
    pandas=0.20.* \
    bokeh=0.12.* && \
    conda clean -tipsy

VOLUME /data
COPY ./app /app

ENTRYPOINT ["bokeh", "serve", "/app"]

# These are some commands
# "--port", "80",
# , "--allow-websocket-origin=$VIRTUAL_HOST"
