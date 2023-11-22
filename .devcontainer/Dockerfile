FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get -y upgrade \
    && apt-get -y install \
        software-properties-common \
        curl \
        unzip \
        bash \
        python3-pip \
        git \
        make \
        libffi-dev \
        jq \
        libpq-dev\
        gcc

# Copy & Install the dependencies file
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH "${PATH}:~/.local/bin"
