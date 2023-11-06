FROM mirekphd/python3.11-ubuntu22.04
MAINTAINER ncf <f18326186224@gmail.com>
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
COPY requirements.txt /tmp
WORKDIR /tmp
RUN  apt-get update \
     && apt-get autoclean \
     && ln -s /usr/bin/pip3.11 /usr/bin/pip && ln -s /usr/bin/python3.11 /usr/bin/python \
     && pip install --upgrade pip \ 
     && pip install -r requirements.txt \
     && rm -rf /var/lib/apt/lists/* && rm /tmp/requirements.txt && mkdir -p /app
WORKDIR /app
ADD . /app
RUN chmod +x /app/entrypoint.sh
CMD ./entrypoint.sh
