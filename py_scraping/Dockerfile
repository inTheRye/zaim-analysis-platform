FROM a1fred/docker-python-phantomjs:latest

ARG AIRFLOW_HOME=/root/airflow

ADD app /app
RUN pip3 install -r /app/requirements.txt

USER root
ENV TZ=Asia/Tokyo

RUN set -ex \
    && apt-get update -yqq \
    && apt-get install -yqq --no-install-recommends \
        netcat \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

COPY script/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["/entrypoint.sh"]
