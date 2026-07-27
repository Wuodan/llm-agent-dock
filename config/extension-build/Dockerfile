# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE

FROM ${BASE_IMAGE} AS runtime

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG EXTENSIONS

RUN --mount=type=bind,source=helpers,target=/tmp/aicage/helpers,readonly \
    --mount=type=bind,source=extensions,target=/tmp/aicage/extensions,readonly \
    /tmp/aicage/helpers/run-selected-extensions.sh ${EXTENSIONS}
