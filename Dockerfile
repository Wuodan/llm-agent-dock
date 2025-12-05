# syntax=docker/dockerfile:1.7-labs
ARG BASE_IMAGE=ubuntu:24.04
ARG TOOL=codex
ARG TARGETARCH=amd64
ARG NODEJS_VERSION=20.17.0

FROM ${BASE_IMAGE} AS runtime

ARG TOOL
ARG TARGETARCH
ARG NODEJS_VERSION

LABEL org.opencontainers.image.title="llm-agent-dock" \
      org.opencontainers.image.description="Multi-base build for agentic developer CLIs" \
      org.opencontainers.image.source="https://github.com/Wuodan/llm-agent-dock" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV DEBIAN_FRONTEND=noninteractive \
    AGENT_TARGETARCH=${TARGETARCH} \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PATH="/root/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin" \
    NPM_CONFIG_PREFIX=/usr/local

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN set -euxo pipefail \
    && if command -v apt-get >/dev/null; then \
         apt-get update; \
         apt-get install -y --no-install-recommends \
           bash \
           bash-completion \
           build-essential \
           ca-certificates \
           curl \
           git \
           gnupg \
           jq \
           locales \
           nano \
           openssh-client \
           pipx \
           python3 \
           python3-pip \
           python3-venv \
           ripgrep \
           sudo \
           tar \
           tini \
           unzip \
           xz-utils \
           zip; \
         rm -rf /var/lib/apt/lists/*; \
       else \
         echo "Unsupported base image for llm-agent-dock; apt-get required" >&2; \
         exit 1; \
       fi \
    && locale-gen en_US.UTF-8 || true

# Install Node.js 20.x (cline core requires >=20).
RUN set -euxo pipefail \
    && case "${TARGETARCH}" in \
         amd64) NODE_DIST_ARCH="x64" ;; \
         arm64) NODE_DIST_ARCH="arm64" ;; \
         *) echo "Unsupported TARGETARCH ${TARGETARCH}" >&2; exit 1 ;; \
       esac \
    && curl -fsSL "https://nodejs.org/dist/v${NODEJS_VERSION}/node-v${NODEJS_VERSION}-linux-${NODE_DIST_ARCH}.tar.xz" \
      | tar -xJ -C /usr/local --strip-components=1 \
    && ln -sf /usr/local/bin/node /usr/bin/node \
    && ln -sf /usr/local/bin/npm /usr/bin/npm \
    && ln -sf /usr/local/bin/npx /usr/bin/npx

# Add new base tweaks here (e.g., base-specific packages or config overrides).

RUN pipx ensurepath >/dev/null 2>&1 || true
RUN python3 -m pip install --break-system-packages --ignore-installed --upgrade pip setuptools wheel
RUN npm config set prefix /usr/local

# Shared workspace directory and convenience symlinks.
RUN mkdir -p /workspace && ln -sf /workspace /root/workspace

# Tool installers -----------------------------------------------------------
RUN --mount=type=bind,source=scripts/installers/,target=/tmp/installers,readonly \
    /tmp/installers/install_${TOOL}.sh

# ARG UID=1000
# ARG GID=1000

# add user
# RUN groupadd -g ${GID} appuser && \
#     useradd -m -u ${UID} -g ${GID} -s /bin/bash appuser

# USER appuser
USER ubuntu

ENV PIPX_HOME=/home/ubuntu/.local/pipx \
    PIPX_BIN_DIR=/home/ubuntu/.local/bin \
    PATH="/home/ubuntu/.local/bin:${PATH}"

RUN PIP_NO_CACHE_DIR=1 \
    pipx install uv \
      --pip-args="--no-cache-dir"

WORKDIR /workspace

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash"]
