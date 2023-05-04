# pull official base image
FROM python:3.11.2-bullseye
# set work directory
WORKDIR /usr/src/app
# install psycopg2 dependencies
RUN apt-get update
RUN apt-get install gcc -y
RUN apt-get install libpq-dev -y
RUN apt-get install postgresql -y
RUN apt-get install postgresql-contrib -y
RUN apt-get install nginx -y
RUN apt-get install supervisor -y
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install dependencies
RUN pip install --upgrade pip
ADD ./requirements.txt .
RUN pip install -r requirements.txt
# copy project
ADD . .
ADD docker_conf/supervisor.conf /etc/supervisor/conf.d/local.supervisor.conf
ADD docker_conf/nginx.conf /etc/nginx/sites-enabled/django_app.conf
EXPOSE 80 22 8000