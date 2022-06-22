ARG PYTHON_VERSION=3.9

FROM python:${PYTHON_VERSION}
RUN mkdir -p /webapp
WORKDIR /webapp

RUN apt-get update && apt-get install -y \
  python3-pip \
  python3-venv \
  python3-dev \
  python3-setuptools \
  python3-wheel
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY py-geolift/dependencies.R .
RUN apt-get install -y r-base
RUN Rscript --verbose dependencies.R

# Install py-geolift
ADD py-geolift /webapp/py-geolift/

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir poetry \
  && cd py-geolift \
  && poetry config virtualenvs.create false \
  && poetry build \
  && pip install dist/pygeolift-*.tar.gz

RUN rm -rf py-geolift

# Install overmind to run two processes at once
RUN apt-get install -y tmux
RUN wget https://github.com/DarthSim/overmind/releases/download/v2.2.2/overmind-v2.2.2-linux-amd64.gz \
  && ln -s /usr/local/bin/overmind-v2.2.2-linux-amd64 /usr/bin/overmind \
  && gunzip -d overmind-v2.2.2-linux-amd64.gz \
  && chmod +x overmind-v2.2.2-linux-amd64

EXPOSE 8080

ADD app/ /webapp/app
RUN ls -al .

# Weird but true, uvicorn fails without click
RUN pip install click
ADD Procfile /webapp/
CMD ["/webapp/overmind-v2.2.2-linux-amd64", "start"]
