FROM python:3.11-slim-buster
LABEL version="1.0" \
     description="tgbot for python3.11" \
     vendor="f18326186224@gmail.com" \
     build-date="2023-11-10"
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
COPY requirements.txt /tmp
WORKDIR /tmp
RUN  apt-get update \
     && apt-get autoclean \
     && pip install --upgrade pip \ 
     && pip install -r requirements.txt \
     && rm -rf /var/lib/apt/lists/* && rm /tmp/requirements.txt && mkdir -p /app
WORKDIR /app
ADD . /app
RUN chmod +x /app/entrypoint.sh
CMD ./entrypoint.sh
