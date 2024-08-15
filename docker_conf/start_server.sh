#!/bin/bash
#
fuser -k 8000/tcp
sleep 2
IS_DEBUG=`/home/django/.env/bin/python /home/django/app/docker_conf/get_docker_env_var.py DEBUG_SERVER`
echo "Debug flag set to:"
echo "$IS_DEBUG"


if [ "$IS_DEBUG" == "DEBUG" ]
then
    echo "Starting manage.py server"
    /home/django/.env/bin/python /home/django/app/django_simple_web_course/manage.py runserver 0.0.0.0:8000
else
    echo "Starting gunicorn server"
    /home/django/.env/bin/gunicorn --bind 0.0.0.0:8000 django_simple_web_course.django_simple_web_course.wsgi
fi