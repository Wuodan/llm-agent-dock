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
RUN /bin/bash <<'EOS'
set -euxo pipefail

install_cline() {
  if npm install -g cline; then
    return
  fi
  cat <<'SHIM' >/usr/local/bin/cline
#!/usr/bin/env bash
set -euo pipefail
echo "cline npm install failed during image build." >&2
echo "Install it inside the container via: npm install -g cline" >&2
exit 1
SHIM
  chmod +x /usr/local/bin/cline
}

install_codex() {
  if npm install -g @openai/codex; then
    return
  fi
  cat <<'SHIM' >/usr/local/bin/codex
#!/usr/bin/env bash
set -euo pipefail
echo "Codex CLI failed to install during build." >&2
echo "Install manually via: npm install -g @openai/codex" >&2
exit 1
SHIM
  chmod +x /usr/local/bin/codex
}

install_factory_ai_droid() {
  local pkg=""
  for candidate in "@factory-ai/droid" "@factoryai/droid-cli" "droid-factory"; do
    if npm install -g "$candidate"; then
      pkg="$candidate"
      break
    fi
  done
  if [[ -n "$pkg" ]]; then
    local target=""
    if command -v droid >/dev/null; then
      target="droid"
    elif command -v factory-ai >/dev/null; then
      target="factory-ai"
    elif command -v droid-factory >/dev/null; then
      target="droid-factory"
    fi
    if [[ -n "$target" ]]; then
      cat <<'WRAP' >/usr/local/bin/factory_ai_droid
#!/usr/bin/env bash
set -euo pipefail
exec TARGET_CMD "$@"
WRAP
      sed -i "s/TARGET_CMD/${target}/" /usr/local/bin/factory_ai_droid
    else
      cat <<'SHIM' >/usr/local/bin/factory_ai_droid
#!/usr/bin/env bash
set -euo pipefail
echo "Factory Droid CLI installed via ${pkg}, but no executable was detected." >&2
echo "Check package docs or install manually inside the container." >&2
exit 1
SHIM
    fi
    chmod +x /usr/local/bin/factory_ai_droid
    return
  fi
  cat <<'SHIM' >/usr/local/bin/factory_ai_droid
#!/usr/bin/env bash
set -euo pipefail
echo "Factory Droid CLI was unavailable during build." >&2
echo "Install via npm (package: @factory-ai/droid) once network access is available." >&2
exit 1
SHIM
  chmod +x /usr/local/bin/factory_ai_droid
}

# Add new agent installers below.
case "${TOOL}" in
  cline) install_cline ;;
  codex) install_codex ;;
  factory_ai_droid) install_factory_ai_droid ;;
  *) echo "Unsupported TOOL '${TOOL}'." >&2; exit 1 ;;
esac
EOS

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
