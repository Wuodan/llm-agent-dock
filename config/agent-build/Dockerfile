# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE
ARG AGENT
ARG IMAGE_SOURCE_URL

FROM ${BASE_IMAGE} AS runtime

ARG AGENT
ARG IMAGE_SOURCE_URL

LABEL org.opencontainers.image.title="aicage" \
      org.opencontainers.image.description="Multi-base build for agentic developer CLIs" \
      org.opencontainers.image.source="${IMAGE_SOURCE_URL}" \
      org.opencontainers.image.licenses="Apache-2.0"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Agent installers
RUN --mount=type=bind,source=agents/,target=/tmp/agents,readonly \
    mkdir -p /tmp/agents-run/${AGENT} && \
    cp -R /tmp/agents/${AGENT}/. /tmp/agents-run/${AGENT}/ && \
    for script in "/tmp/agents-run/${AGENT}"/*.sh; do \
      sed -i 's/\r$//' "$script"; \
      chmod +x "$script"; \
    done && \
    /tmp/agents-run/${AGENT}/install.sh && \
    rm -rf /tmp/agents-run && \
    npm cache clean --force && \
    pip cache purge

ENV AGENT=${AGENT}

# entrypoint.sh uses this variable
ENV AICAGE_ENTRYPOINT_CMD=${AGENT}
