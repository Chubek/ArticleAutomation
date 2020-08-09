# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:3.0-python3.8-appservice
FROM python:latest
FROM ubuntu:latest

RUN apt-get clean \
&& apt-get update \
&& apt-get install sudo -y \
&& apt-get install apt-transport-https -y \
&& sudo apt-get install unixodbc -y \
&& sudo apt-get install unixodbc-dev -y \
&& sudo apt-get install curl -y \
&& sudo apt-get install poppler-utils -y \
&& sudo apt-get install --reinstall build-essential -y


RUN echo "Set disable_coredump false" >> /etc/sudo.conf

RUN sudo su
RUN sudo curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN sudo curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN sudo apt-get update
RUN sudo ACCEPT_EULA=Y apt-get install msodbcsql17
RUN sudo ACCEPT_EULA=Y apt-get install mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc


COPY requirements.txt /
ADD requirements.txt /
COPY data_jar_scrape.py /
ADD data_jar_scrape.py /

RUN sudo apt install python3-pip -y

RUN pip3 install -r /requirements.txt

CMD [ "python3", "./data_jar_scrape.py" ]
