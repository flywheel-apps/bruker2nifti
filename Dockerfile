FROM python:2.7.15-alpine3.8
RUN apk add --no-cache build-base python-dev bash && pip install numpy bruker2nifti
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

COPY run.py ${FLYWHEEL}/run.py
