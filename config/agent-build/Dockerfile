# syntax=docker/dockerfile:1.7-labs
ARG BASE_IMAGE=base
ARG AGENT=codex

FROM ${BASE_IMAGE} AS runtime

ARG AGENT

LABEL org.opencontainers.image.title="aicage" \
      org.opencontainers.image.description="Multi-base build for agentic developer CLIs" \
      org.opencontainers.image.source="https://github.com/aicage/aicage-image" \
      org.opencontainers.image.licenses="Apache-2.0"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Agent installers ----------------------------------------------------------
RUN --mount=type=bind,source=agents/,target=/tmp/agents,readonly \
    /tmp/agents/${AGENT}/install.sh

ENV AGENT=${AGENT}
CMD ["sh", "-c", "$AGENT"]
