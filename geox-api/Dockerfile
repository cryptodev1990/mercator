# Builds app for deployment
ARG PYTHON_VERSION=3.9

# Build just in a different stage and copy the executable later
# to minimize the size of the final image
FROM rust:bullseye as builder
RUN cargo install just


FROM python:${PYTHON_VERSION}

# Dockerfile for mercator FastAPI backend.
# Derived from https://fastapi.tiangolo.com/deployment/docker/?h=containers
WORKDIR /code

# gdal is needed for fiona
RUN apt-get update \
    && apt-get install -y libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
# silences this warning:
# WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager.
# It is recommended to use a virtual environment instead
ENV PIP_ROOT_USER_ACTION=ignore
COPY ./requirements.txt /webapp/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade "pip==22.3.1" "wheel==0.38.3" && \
    pip install --no-cache-dir --upgrade -r /webapp/requirements.txt

# Install overmind
ENV OVERMIND_VERSION ${OVERMIND_VERSION:-2.2.2}
RUN apt-get update \
    && apt-get install -y tmux \
    && rm -rf /var/lib/apt/lists/* \
    && wget https://github.com/DarthSim/overmind/releases/download/v${OVERMIND_VERSION}/overmind-v${OVERMIND_VERSION}-linux-amd64.gz -O overmind.gz \
    && gunzip -d overmind.gz \
    && mv overmind /usr/local/bin/overmind \
    && chmod +x /usr/local/bin/overmind

# Copy just executable from builder stage
COPY --from=builder /usr/local/cargo/bin/just /usr/local/bin/just

WORKDIR /webapp

RUN DD_API_KEY=MY_DD_API_KEY_PLACEHOLDER DD_INSTALL_ONLY=true bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"

COPY ./app /webapp/app
COPY ./cli /webapp/cli
COPY ./alembic /webapp/alembic
COPY ./start.sh ./worker-start.sh ./alembic.ini ./Procfile ./hypercorn.toml ./justfile /webapp/

# ARG have to be after FROM to be read
# This sets GIT_COMMIT in two ways - default env variable (expected not to be overwritten)
# and in the file - .env.
ARG git_commit_hash
ENV GIT_COMMIT=${git_commit_hash}
ENV APP_ENV=production
RUN touch /webapp/.env && \
    echo "GIT_COMMIT=$GIT_COMMIT" >> /webapp/.env

# copy in datadog config files
RUN mkdir /etc/datadog-agent/conf.d/python.d
COPY --chown=dd-agent:dd-agent --chmod=0777 ./datadog-python-conf.yaml /etc/datadog-agent/conf.d/python.d/conf.yaml
COPY --chown=dd-agent:dd-agent --chmod=0777 ./datadog-security-agent.yaml /etc/datadog-agent/security-agent.yaml
COPY --chown=dd-agent:dd-agent --chmod=0777 ./datadog.yaml /etc/datadog-agent/datadog.yaml

EXPOSE 8080
ENV PYTHONPATH=/webapp
ENV APP_RELOAD=
CMD ["overmind", "start"]
