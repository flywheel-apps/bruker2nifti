FROM python:2.7.15-alpine3.8
RUN apk add --no-cache build-base python-dev bash && pip install numpy bruker2nifti
COPY run.py /app/run.py
ENTRYPOINT [ "/bin/bash" ]
