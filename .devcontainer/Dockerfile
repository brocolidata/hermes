FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update \
    && apt-get -y upgrade \
    && apt install -y -V ca-certificates lsb-release wget \
    && wget https://apache.jfrog.io/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb \
    && apt install -y -V ./apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb

RUN apt-get -y update && apt-get -y upgrade \
    && apt-get -y install \
        software-properties-common \
        curl \
        zip \
        unzip \
        bash \
        python3-pip \
        git \
        cmake \
        make \
        libffi-dev \
        jq \
        libpq-dev\
        gcc \
        libarrow-dev

# Copy & Install the dependencies file
COPY requirements.txt .
RUN pip install -r requirements.txt --break-system-packages

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${PATH}:~/.local/bin"
