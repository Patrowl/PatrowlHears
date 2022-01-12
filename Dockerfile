FROM python:3.7-slim
MAINTAINER Patrowl.io "getsupport@patrowl.io"
LABEL Name="PatrowlHears" Version="1.1.0"

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/patrowl-hears/
WORKDIR /opt/patrowl-hears/

RUN apt-get update -yq \
	&& apt-get install -yq --no-install-recommends \
		apt-utils \
		python3 \
		python3-pip \
		libmagic-dev \
		python3-psycopg2 \
		python3-dev \
		libpq-dev \
		gcc \
		git \
		wget \
	&& apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . /opt/patrowl-hears/
COPY backend_app/backend_app/settings.py.sample /opt/patrowl-hears/backend_app/backend_app/settings.py

WORKDIR /opt/patrowl-hears/backend_app
RUN rm -rf env \
	&& python --version \
	&& pip3 install virtualenv \
	&& virtualenv env \
  && /opt/patrowl-hears/backend_app/env/bin/pip3 install -r /opt/patrowl-hears/backend_app/requirements.txt

WORKDIR /opt/patrowl-hears/

EXPOSE 8303
ENTRYPOINT ["/opt/patrowl-hears/docker-entrypoint.sh"]
CMD ["run"]
