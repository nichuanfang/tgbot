FROM python:3.11-buster
MAINTAINER ncf <f18326186224@gmail.com>
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
COPY requirements.txt /tmp
# 修改hosts文件
COPY hosts /etc/hosts
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
