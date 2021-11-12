FROM continuumio/miniconda:4.7.12

LABEL MAINTAINER="Steven W. Tolbert <stolb002@fiu.edu>" 
LABEL MAINTAINER="Farukh Saidmuratov <fsaidmur@fiu.edu>" 

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update --allow-releaseinfo-change && apt-get install -y  \
 build-essential \
 bash-completion=1:2.8-6 \
 git=1:2.20.1-2+deb10u3 \
 locales=2.28-10 \
 sudo=1.8.27-1+deb10u3 \
 nano=3.2-3 \
 && rm -rf /var/lib/apt/lists/* && apt-get clean

RUN locale-gen en_US.UTF-8

WORKDIR /tmp

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml && conda clean -afy

# Disable password and not ask for finger info
RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu

WORKDIR /projects
