FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Kyiv

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    lsb-release \
    python3 \
    python3-pip \
    sudo \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash builder \
    && echo 'builder ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && echo 'Defaults env_keep += "DEBIAN_FRONTEND TZ"' >> /etc/sudoers

WORKDIR /workspace

RUN git clone --depth 1 https://github.com/ArduPilot/ardupilot.git /opt/ardupilot \
    && chown -R builder:builder /opt/ardupilot \
    && sudo -u builder -H bash -lc 'cd /opt/ardupilot && Tools/environment_install/install-prereqs-ubuntu.sh -y' \
    && sudo -u builder -H bash -lc 'cd /opt/ardupilot && git submodule update --init --recursive && ./waf configure --board sitl && ./waf copter'

COPY requirements.txt /workspace/requirements.txt
RUN pip3 install --no-cache-dir --index-url https://pypi.org/simple -r /workspace/requirements.txt

COPY src /workspace/src
COPY scripts /workspace/scripts
RUN chmod +x /workspace/scripts/*.sh

CMD ["bash", "scripts/run-local.sh"]
