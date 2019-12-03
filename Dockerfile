FROM python:3.7.2

WORKDIR /src

ADD . /src
RUN pip install -r requirements.txt

# keep a long timeout to support queries of long duration
ENTRYPOINT gunicorn -w4 -b 0.0.0.0:5000 main:app --timeout 120