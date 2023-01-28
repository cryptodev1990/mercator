# Builds app for deployment
ARG PYTHON_VERSION=3.9

# Build just in a different stage and copy the executable later
# to minimize the size of the final image
FROM rust:bullseye as builder
RUN cargo install just

FROM python:${PYTHON_VERSION}

# Install python dependencies
# silences this warning:
# WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager.
# It is recommended to use a virtual environment instead
ENV PIP_ROOT_USER_ACTION=ignore
COPY ./requirements.txt /requirements.txt
RUN python -m pip install --no-cache-dir --upgrade "pip==22.3.1" "wheel==0.38.3" && \
    pip install --no-cache-dir --upgrade -r /requirements.txt

# Copy just executable from builder stage
COPY --from=builder /usr/local/cargo/bin/just /usr/local/bin/just

RUN DD_API_KEY=MY_DD_API_KEY_PLACEHOLDER DD_INSTALL_ONLY=true bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script_agent7.sh)"

RUN mkdir /app
COPY ./api /app/api
COPY scripts/run.sh justfile /app

# copy in datadog config files
RUN mkdir /etc/datadog-agent/conf.d/python.d
COPY --chown=dd-agent:dd-agent --chmod=0777 ./datadog-python-conf.yaml /etc/datadog-agent/conf.d/python.d/conf.yaml
COPY --chown=dd-agent:dd-agent --chmod=0777 ./datadog-security-agent.yaml /etc/datadog-agent/security-agent.yaml
COPY --chown=dd-agent:dd-agent --chmod=0777 ./datadog.yaml /etc/datadog-agent/datadog.yaml

WORKDIR /app
EXPOSE 8080
ENV APP_ENV=production
ENV PYTHONPATH=/app
ENV APP_RELOAD=
CMD ["bash", "run.sh"]
