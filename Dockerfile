FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install -y python3-pip tcpdump iputils-ping

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .

ENTRYPOINT [ "python3", "main.py" ]
