FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bzip2 \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PATH /opt/conda/bin:$PATH
RUN echo "PATH=/opt/conda/bin:$PATH" > /etc/environment && \
    wget --quiet http://repo.continuum.io/miniconda/Miniconda3-4.3.21-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

RUN conda config --set always_yes True && \
    conda config --system --prepend channels conda-forge && \
    conda config --set auto_update_conda False

RUN conda install --quiet \
    jupyter=1.0.* \
    beautifulsoup4=4.6.* \
    pandas=0.20.* \
    requests=2.14.* \
    matplotlib=2.0* && \
    conda remove --quiet --force qt pyqt && \
    conda clean -tipsy

VOLUME /project
WORKDIR /project

# Note the timeout value set to None. This notebook may take a while so we shouldn't rush the cells
CMD ["jupyter", "nbconvert", "--ExecutePreprocessor.timeout=None", "--to=notebook", "--output", "TimeSheetData.ipynb", "--execute", "TimeSheetData.ipynb"]

