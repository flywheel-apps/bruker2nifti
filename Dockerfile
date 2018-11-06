FROM continuumio/anaconda:5.3.0
RUN pip install bruker2nifti
COPY run.py /app/run.py
