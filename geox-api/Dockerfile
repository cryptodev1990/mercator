ARG PYTHON_VERSION=3.9

FROM python:${PYTHON_VERSION}
RUN mkdir -p /app
WORKDIR /app

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
COPY . .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir poetry \
 && poetry config virtualenvs.create false \
 && cd py-geolift \
 && poetry build \
 && pip install dist/pygeolift-*.tar.gz

RUN rm -rf py-geolift

EXPOSE 8080

# Weird but true, uvicorn fails without click
RUN pip install click
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
