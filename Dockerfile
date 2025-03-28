FROM python:3.12-slim  

ENV SNAPSHOT_INTERVAL='30'
ENV DAILY_VIDEO_TIME='08:00'
ENV DIR='/srv/whetupulse/'

ENV TZ=America/Chicago

RUN apt-get update && \
    apt-get install --yes --no-install-recommends &&\
    apt-get install -y ffmpeg &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#############################################################################
# Update pip and setuptools to ensure compatibility with Python 3.12
RUN python -m ensurepip --upgrade && \
    python -m pip install --upgrade pip setuptools wheel
#############################################################################

# Install and Update Python Packages
COPY requirements.txt /tmp/requirements.txt
#RUN pip install -r /tmp/requirements.txt
RUN pip install --default-timeout=1000 -r /tmp/requirements.txt

# Copy over the Python Project
COPY ./app/ /srv/whetupulse/

RUN mkdir /srv/whetupulse/images/
RUN mkdir /srv/whetupulse/output/

WORKDIR /srv/whetupulse/

ENTRYPOINT ["python","-u","app.py"]