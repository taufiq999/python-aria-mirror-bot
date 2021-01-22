FROM ubuntu:20.04

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app
RUN DEBIAN_FRONTEND="noninteractive" \
    apt-get -qq update && apt-get -qq install -y tzdata \
    aria2 git python3 python3-pip locales python3-lxml \
    curl pv jq ffmpeg p7zip-full p7zip-rar
COPY requirements.txt .
COPY extract /usr/local/bin
COPY pextract /usr/local/bin
RUN pip3 install --no-cache-dir -r requirements.txt && \
    apt-get -qq purge git
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
COPY . .
COPY netrc /root/.netrc
RUN chmod +x /usr/local/bin/extract && chmod +x /usr/local/bin/pextract && \
    chmod +x aria.sh

CMD ["bash","start.sh"]
