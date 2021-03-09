FROM ubuntu:20.04

MAINTAINER Steven W. Tolbert <stolb002@fiu.edu> 

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y upgrade\
 bash-completion \
 build-essential \
 curl \
 git \
 git-core \
 golang \
 htop \
 locales \
 man \
 nmap \
 python3-pip \
 ruby-full \
 strace \
 sudo \
 tig \
 vim \
 wget

RUN locale-gen en_US.UTF-8

COPY requirements.txt /tmp
WORKDIR /tmp
RUN pip3 install -r requirements.txt

# Disable password and not ask for finger info
RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu


WORKDIR /home/ubuntu

