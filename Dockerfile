FROM python:2.7
LABEL maintainer "scott@mux.com"

# Install dependencies
RUN pip install python-dateutil

ADD coreos-release-notifier.py /

ENTRYPOINT ["python2", "/coreos-release-notifier.py"]
