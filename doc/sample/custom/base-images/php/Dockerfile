# check=skip=InvalidDefaultArgInFrom

# ## Installation equals to aicage builtin base-images ##
#
# Download os-installer scripts from `aicage-image-base` and run all of them
#
# Simply set this variable below to match a folder in:
# https://github.com/aicage/aicage-image-base/tree/main/scripts/os-installers/distro

ARG AICAGE_INSTALL_DISTRO=debian

ARG FROM_IMAGE

FROM ${FROM_IMAGE} AS from_image

ARG AICAGE_INSTALL_DISTRO

LABEL org.opencontainers.image.title="Custom aicage-image-base" \
      org.opencontainers.image.description="Locally built base layer for agent images" \
      org.opencontainers.image.source="https://github.com/aicage/aicage-custom-samples" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    NPM_CONFIG_PREFIX=/usr/local \
    PIPX_HOME=/opt/pipx \
    PIPX_BIN_DIR=/opt/pipx/bin \
    PATH="/opt/pipx/bin:/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin"

# Run installer setup as root.
USER 0

ARG AICAGE_IMAGE_BASE_DIR=/tmp/aicage-image-base

RUN --mount=type=bind,source=helpers,target=/tmp/aicage/helpers,readonly \
    mkdir -p /tmp/aicage/helpers-run && \
    cp /tmp/aicage/helpers/*.sh /tmp/aicage/helpers-run/ && \
    for script in /tmp/aicage/helpers-run/*.sh; do \
      sed -i 's/\r$//' "$script"; \
      chmod +x "$script"; \
    done && \
    echo "Setup: Install prerequisites ..." && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      tar && \
    \
    echo "Setup: Downloading installation scripts from 'github.com/aicage/aicage-image-base' ..." && \
    /tmp/aicage/helpers-run/install-cosign.sh && \
    /tmp/aicage/helpers-run/get-aicage-release-artifact.sh aicage-image-base "${AICAGE_IMAGE_BASE_DIR}" && \
    \
    echo "Install: Running os-installer scripts for distro '${AICAGE_INSTALL_DISTRO}' ..." && \
    "${AICAGE_IMAGE_BASE_DIR}/scripts/os-installers/distro/${AICAGE_INSTALL_DISTRO}/install.sh" && \
    \
    echo "Install: Copy aicage entrypoint.sh ..." && \
    cp "${AICAGE_IMAGE_BASE_DIR}"/scripts/entrypoint.sh /usr/local/bin/entrypoint.sh && \
    \
    echo "Clean up: Remove downloaded files ..." && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* && \
    rm -rf "${AICAGE_IMAGE_BASE_DIR}" && \
    rm -rf /tmp/aicage/helpers-run

ENV AICAGE_ENTRYPOINT_CMD=bash

# Use tini from PATH to work across distros (e.g. Alpine installs it in /sbin).
ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]
