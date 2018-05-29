FROM gliderlabs/alpine:3.4

MAINTAINER Adrian Agnic

RUN apk add --no-cache python3 && \
  python3 -m ensurepip && \
  rm -r /usr/lib/python*/ensurepip && \
  pip3 install --upgrade pip setuptools && \
  if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
  rm -r /root/.cache

RUN apk add --no-cache python3-dev
RUN apk add --no-cache alpine-sdk
RUN pip3 install pycrypto

WORKDIR /app
COPY . /app

ENTRYPOINT ["python3", "tcp/mserver.py"]