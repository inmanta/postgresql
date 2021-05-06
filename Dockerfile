FROM postgres:10

ARG BUILDDIR="/tmp/build"
ARG PYTHON_VER="3.6.11"
WORKDIR ${BUILDDIR}

RUN apt-get update -qq && \
apt-get upgrade -y
RUN apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev curl libbz2-dev
RUN apt-get install wget gcc make zlib1g-dev -y -qq > /dev/null 2>&1 && \
wget --quiet https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz > /dev/null 2>&1 && \
tar zxf Python-${PYTHON_VER}.tgz && \
cd Python-${PYTHON_VER} && \
./configure  > /dev/null 2>&1 && \
make > /dev/null 2>&1 && \
make install > /dev/null 2>&1 && \
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

RUN python3 -m venv env
RUN env/bin/pip install -U pip

COPY requirements.freeze requirements.freeze
COPY requirements.dev.txt requirements.dev.txt
RUN env/bin/pip install -r requirements.dev.txt -c requirements.freeze

COPY module.yml module.yml
COPY model model
COPY templates templates
COPY plugins plugins
COPY tests tests

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
