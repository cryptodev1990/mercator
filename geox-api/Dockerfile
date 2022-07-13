ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}

# Dockerfile for mercator FastAPI backend.
# Derived from https://fastapi.tiangolo.com/deployment/docker/?h=containers
WORKDIR /webapp

COPY ./requirements.txt /webapp/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /webapp/requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /webapp/requirements-dev.txt

COPY ./app /webapp/app

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
