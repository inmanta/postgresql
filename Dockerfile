ARG PG_MAJOR_VERSION
FROM postgres:${PG_MAJOR_VERSION}-bullseye
ARG PG_MAJOR_VERSION
ARG PYTHON_VER

# Store the Postgres major version into an env variable to make it available from within the tests
ENV PG_MAJOR_VERSION=${PG_MAJOR_VERSION}

ARG BUILDDIR="/tmp/build"
ARG PIP_INDEX_URL
ARG PIP_PRE
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR ${BUILDDIR}

RUN apt-get update -qq
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev curl libbz2-dev
RUN apt-get install wget gcc make zlib1g-dev -y -qq > /dev/null 2>&1 && \
    wget --quiet https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz > /dev/null 2>&1 && \
    tar zxf Python-${PYTHON_VER}.tgz && \
    cd Python-${PYTHON_VER} && \
    ./configure  > /dev/null 2>&1 && \
    make > /dev/null 2>&1 && \
    make install > /dev/null 2>&1 && \
    cd "$(dirname "$(which python3)")" && \
    ln -s python3 python && \
    rm -rf ${BUILDDIR}

RUN apt-get install -y openssh-server sudo git supervisor python3-venv

RUN mkdir /var/run/sshd
RUN mkdir /root/.ssh; chown root. /root/.ssh; chmod 700 /root/.ssh
RUN cat /dev/zero | ssh-keygen -q -N ""
RUN cp ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys

RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /module/postgresql
WORKDIR /module/postgresql

# Copy the entire module into the container
COPY . .

RUN rm -rf env && python3 -m venv env && env/bin/pip install -U pip
# The module set tests convert the module into a V2 module, install it in the test
# environment and run the tests against it. This code ensures that the module is
# installed as a V2 module when it contains a inmanta_plugins directory.
RUN if [ -e "inmanta_plugins" ]; then \
    env/bin/pip install -r requirements.dev.txt -c requirements.freeze; \
    rm -rf ./dist; \
    env/bin/inmanta module build; \
    env/bin/pip install -c requirements.freeze ./dist/*.whl; \
    else \
    env/bin/pip install -r requirements.dev.txt -c requirements.freeze; \
    fi

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
