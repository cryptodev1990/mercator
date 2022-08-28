My problem: I need to be able to connect to my Postgres database with 3rd party cloud services and can't.

My app is which is built on top of Fly, which itself is a wrapper around AWS. It aims to be a more modern Heroku--
you take a Dockerfile, and Fly converts it to a VM. They also make it easy to spin up a Postgres
database, and any application you create through Fly is instantly on the same VPC as all the other applications there.

I need to copy data from that Postgres instance (which is on a private network) to an S3 bucket that I control.

In other words, I need to copy the contents of my Postgres database out of Fly. I was hoping to use
Postgres change data capture through a tool called FiveTran but at this point will accept whatever.

Options:

1) Create a Celery task that wholesale copies the table that I'd like replicated into S3.
  - Pro: I know this works and I could get it done in a day
  - Con: Skips CDC, so it might be a bit slower. More code to write/maintain. Might actually get expensive.
2) Expose my Postgres database on Fly to the public internet
  - Pro: Can instantly connect with any of the 3rd party tools
  - Con: It doesn't seem secure, I don't think the traffic is actually encrypted
3) Use a reverse SSH tunnel to connect to FiveTran. Have Fly.io run the reverse SSH tunnel
  - Pro: Security is stronger, since the SSH tunnel will only be available through a PEM
  - Con: I don't actually know how to do it, although I see some similar solutions on the Fly message boards for a tool called Hightouch.

```
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
```

4) Are there simpler/better solutions, e.g.
  - Deploy pgbouncer and connect to it? https://community.fly.io/t/how-to-setup-and-use-pgbouncer-with-fly-postgres/3035
  - Use AWS RDS on a VPC configured to communicate with Fly.io: https://github.com/fly-apps/rds-connector
  - Peer an EC2 with Wireguard and tunnel into that EC2 (Fivetran can tunnel)
  - Use Hightouch and copy the example from the message boards--trying this but getting an error
