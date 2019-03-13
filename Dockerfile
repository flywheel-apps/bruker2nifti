FROM python:3.7.2-alpine3.9
MAINTAINER Flywheel <support@flywheel.io>
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}
RUN set -eux \
    && apk add --no-cache \
        bash \
        build-base \
    && pip install bruker2nifti \
    && mkdir -p ${FLYWHEEL}/input ${FLYWHEEL}/output
COPY manifest.json manifest.json
COPY run run
ENTRYPOINT ["/flywheel/v0/run"]
