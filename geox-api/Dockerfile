ARG PYTHON_VERSION=3.7

FROM python:${PYTHON_VERSION}

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel
RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Install py-geolift
RUN apt-get install -y r-base
RUN Rscript --verbose py-geolift/dependencies.R

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir poetry \
 && poetry config settings.virtualenvs.create false \
 && cd py-geolift \
 && poetry install --no-dev \
 && pip uninstall --yes poetry

RUN rm -rf py-geolift

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
