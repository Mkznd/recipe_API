FROM python
MAINTAINER Mike Uzundai

ENV PYTHONUNBUFFERED 1

COPY ./requirments.txt /requirments.txt
RUN pip install -r /requirments.txt

RUN mkdir /app
WORKDIR ./app
COPY ./app /app

RUN adduser --disabled-password user
USER user