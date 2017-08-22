FROM continuumio/miniconda

RUN conda config --set always_yes True && \
    conda config --system --append channels conda-forge && \
    conda config --set auto_update_conda False

RUN conda install --quiet \
    pandas=0.20.* \
    bokeh=0.12.* && \
    conda clean -tipsy

VOLUME bokeh
WORKDIR bokeh

# ENV VIRTUAL_HOST vps441625.ovh.net
# ENV VIRTUAL_PROTO uwsgi
# EXPOSE 80

# CMD ["bokeh", "serve", "--port", "80", "examples/app/sliders.py"]
# , "--allow-websocket-origin=vps441625.ovh.net"
# "--port", "80",
