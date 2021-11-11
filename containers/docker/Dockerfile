FROM continuumio/miniconda3:4.7.12

LABEL MAINTAINER="Steven W. Tolbert <stolb002@fiu.edu>" 
LABEL MAINTAINER="Farukh Saidmuratov <fsaidmur@fiu.edu>" 

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y  \
 build-essential \
 bash-completion=1:2.8-6 \
 curl=7.64.0-4+deb10u2 \
 git=1:2.20.1-2+deb10u3 \
 golang=2:1.11~1 \
 locales=2.28-10 \
 python3-pip=18.1-5 \
 sudo=1.8.27-1+deb10u3 \
 nano=3.2-3 \
 wget=1.20.1-1.1 \
 && rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US.UTF-8

WORKDIR /tmp

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Disable password and not ask for finger info
RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu

WORKDIR /projects