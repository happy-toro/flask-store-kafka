FROM python:3.9-alpine
WORKDIR /app

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY requirements.txt .
# create and activate python virtual environment 
RUN python -m venv venv
RUN source venv/bin/activate
# install the necessary python packages into 
# virtual environment 
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    build-base \
    linux-headers \
    pcre-dev \
    postgresql-dev \
    libffi-dev \
    librdkafka-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del --no-cache .build-deps 
# install additional runtime into container OS 
# pcre is required by uwsgi
# libpq is required by psycopg2
# libffi is required by cryptography
RUN apk add pcre libpq libffi librdkafka
# create log directory for uwsgi logging
RUN mkdir log

COPY . .
EXPOSE 80
CMD ["uwsgi", "uwsgi.ini"]