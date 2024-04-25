FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG REQUIREMENTS

WORKDIR /code

COPY ./authentication /code
RUN python -m pip install --no-cache-dir -r ${REQUIREMENTS}
