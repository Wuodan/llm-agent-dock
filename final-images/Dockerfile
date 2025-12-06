# syntax=docker/dockerfile:1.7-labs
ARG BASE_IMAGE=wuodan/aicage-base:ubuntu-base-dev
ARG TOOL=codex

FROM ${BASE_IMAGE} AS runtime

ARG TOOL

LABEL org.opencontainers.image.title="aicage" \
      org.opencontainers.image.description="Multi-base build for agentic developer CLIs" \
      org.opencontainers.image.source="https://github.com/Wuodan/aicage" \
      org.opencontainers.image.licenses="Apache-2.0"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Tool installers -----------------------------------------------------------
RUN --mount=type=bind,source=scripts/installers/,target=/tmp/installers,readonly \
    /tmp/installers/install_${TOOL}.sh

COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["bash"]
