# Builds app for deployment
# See https://fastapi.tiangolo.com/deployment/docker/#docker-image-with-poetry
FROM python:3.10 as requirements-stage

WORKDIR /tmp

RUN pip install poetry --update
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

WORKDIR /app

EXPOSE 8080
COPY start.sh .

CMD ["./start.sh"]
