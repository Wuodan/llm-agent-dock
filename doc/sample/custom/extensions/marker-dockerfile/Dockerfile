# check=skip=InvalidDefaultArgInFrom
ARG BASE_IMAGE

FROM ${BASE_IMAGE} AS runtime

RUN mkdir -p /usr/local/share/aicage-extensions \
    && echo "marker" >/usr/local/share/aicage-extensions/marker.txt
