# pull official base image
FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive

# install psycopg2 dependencies
RUN apt-get update
RUN apt-get install curl -y
RUN apt-get install python3 -y
RUN apt-get install python-is-python3
RUN apt-get install gcc -y
RUN apt-get install libpq-dev -y
RUN apt-get install vim -y
RUN apt-get install postgresql-contrib -y
RUN apt-get install nginx -y
RUN apt-get install supervisor -y
RUN apt-get install python3-pip -y
RUN apt-get install psmisc -y
RUN apt-get install git -y
RUN apt-get install python3-venv -y
RUN apt-get install vim -y
RUN apt-get install -y nmap
RUN apt-get install -y netcat
RUN apt-get install -y libgirepository1.0-dev 
RUN apt-get install -y libpango1.0-0

RUN [ -e /etc/nginx/sites-enabled/default ] && rm /etc/nginx/sites-enabled/default

RUN useradd -ms /bin/bash django
RUN mkdir -p /var/www/static_root
RUN chown django /var/www/static_root

RUN mkdir -p /home/django/app
WORKDIR /home/django/app
ADD . .
RUN python3 -m venv /home/django/.env

# change ownership of django dir
RUN chown -R django /home/django/app
# this probably shouldn't be 777 no time to troubleshoot
RUN chmod -R 777 /home/django/app
RUN chown -R django /home/django/.env
RUN chown -R django /var/log

# change ownership of nginx dirs
RUN chown -R www-data:www-data /etc/nginx
RUN chown -R www-data:www-data /var/lib/nginx
RUN chmod -R 777 /var/lib/nginx

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN /home/django/.env/bin/pip install --upgrade pip
ADD ./requirements.txt .
RUN /home/django/.env/bin/pip install -r requirements.txt

# copy project configurations
ADD docker_conf/app.supervisor.conf /etc/supervisor/conf.d/app.supervisor.conf
ADD docker_conf/site.conf /etc/nginx/sites-enabled/django_app.conf
ADD docker_conf/nginx.conf /etc/nginx/nginx.conf
ADD docker_conf/supervisord.conf /etc/supervisor/supervisord.conf
USER django

EXPOSE 80 22 8000