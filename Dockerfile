FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

RUN pip3 install streamlit py2neo folium