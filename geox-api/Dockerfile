# Builds app for deployment
ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}

# Dockerfile for mercator FastAPI backend.
# Derived from https://fastapi.tiangolo.com/deployment/docker/?h=containers
WORKDIR /webapp

COPY ./requirements.txt /webapp/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip==22.1.2 && \
    pip install --no-cache-dir --upgrade -r /webapp/requirements.txt

COPY ./app /webapp/app
COPY ./alembic /webapp/alembic
COPY ./start.sh ./alembic.ini /webapp/

# WARNING=ARG have to be after FROM to be read
ARG git_commit_hash
ENV GIT_COMMIT=${git_commit_hash}
RUN touch /webapp/.env &&  \
    echo "GIT_COMMIT=$GIT_COMMIT" >> /webapp/.env

EXPOSE 8080
ENV PYTHONPATH=/webapp
ENV APP_RELOAD=
CMD ["./start.sh"]
