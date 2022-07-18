# Builds app for deployment
ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}

# Dockerfile for mercator FastAPI backend.
# Derived from https://fastapi.tiangolo.com/deployment/docker/?h=containers
WORKDIR /webapp

COPY ./requirements.txt /webapp/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /webapp/requirements.txt

COPY ./app /webapp/app
COPY ./alembic /webapp/alembic
COPY ./start.sh ./alembic.ini /webapp/

EXPOSE 8080
ENV PYTHONPATH=/webapp APP_RELOAD=
CMD ["./start.sh"]
