FROM alpine:latest

RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk update

RUN apk add --update openssh-client && apk add autossh && rm -rf /var/cache/apk/*
ADD ./key.pem key.pem

CMD autossh -M 0 -i key.pem \
    -R 0.0.0.0:57887:168.220.98.6:5433 \
    tunnel.us-east-1.hightouch.io -p 49344 \
      -o ExitOnForwardFailure=yes \
      -o HostKeyAlgorithms=+ssh-rsa \
      -o PubkeyAcceptedAlgorithms=+ssh-rsa \
      -o "ServerAliveInterval 30" \
      -o StrictHostKeyChecking=no
