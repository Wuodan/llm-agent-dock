# syntax=docker/dockerfile:1.7-labs
ARG BASE_IMAGE=ubuntu:24.04
ARG TOOL=codex
ARG TARGETARCH=amd64

FROM ${BASE_IMAGE} AS runtime

ARG TOOL
ARG TARGETARCH

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
           ca-certificates \
           curl \
           git \
           gnupg \
           jq \
           locales \
           nano \
           nodejs \
           npm \
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

# Add new base tweaks here (e.g., base-specific packages or config overrides).

RUN pipx ensurepath >/dev/null 2>&1 || true
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN npm config set prefix /usr/local

# Shared workspace directory and convenience symlinks.
RUN mkdir -p /workspace && ln -sf /workspace /root/workspace

# Tool installers -----------------------------------------------------------
RUN set -euxo pipefail \
    && install_cline() { \
         if npm install -g cline; then \
           return; \
         fi; \
         cat <<'SHIM' >/usr/local/bin/cline; \
#!/usr/bin/env bash
set -euo pipefail
echo "cline npm install failed during image build." >&2
echo "Install it inside the container via: npm install -g cline" >&2
exit 1
SHIM
         chmod +x /usr/local/bin/cline; \
       }; \
    install_codex() { \
         if npm install -g @openai/codex; then \
           return; \
         fi; \
         cat <<'SHIM' >/usr/local/bin/codex; \
#!/usr/bin/env bash
set -euo pipefail
echo "Codex CLI failed to install during build." >&2
echo "Install manually via: npm install -g @openai/codex" >&2
exit 1
SHIM
         chmod +x /usr/local/bin/codex; \
       }; \
    install_factory_ai_droid() { \
         local pkg=""; \
         for candidate in "@factory-ai/droid" "@factoryai/droid-cli" "droid-factory"; do \
           if npm install -g "$candidate"; then \
             pkg="$candidate"; \
             break; \
           fi; \
         done; \
         if [[ -n "$pkg" ]]; then \
           if command -v droid >/dev/null; then \
             cat <<'WRAP' >/usr/local/bin/factory_ai_droid; \
#!/usr/bin/env bash
set -euo pipefail
exec droid "$@"
WRAP
             chmod +x /usr/local/bin/factory_ai_droid; \
           fi; \
           return; \
         fi; \
         cat <<'SHIM' >/usr/local/bin/factory_ai_droid; \
#!/usr/bin/env bash
set -euo pipefail
echo "Factory Droid CLI was unavailable during build." >&2
echo "Install via npm (package: @factory-ai/droid) once network access is available." >&2
exit 1
SHIM
         chmod +x /usr/local/bin/factory_ai_droid; \
       }; \
    # Add new agent installers below.
    case "${TOOL}" in \
      cline) install_cline ;; \
      codex) install_codex ;; \
      factory_ai_droid) install_factory_ai_droid ;; \
      *) echo "Unsupported TOOL '${TOOL}'." >&2; exit 1 ;; \
    esac

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash"]
