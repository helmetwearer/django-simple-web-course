#!/bin/bash
trap "{fuser -k 8000/tcp; exit 0;}" EXIT
fuser -k 8000/tcp
sleep 2
IS_DEBUG=`python /usr/src/app/docker_conf/get_docker_env_var.py DEBUG_SERVER`
echo "Debug flag set to:"
echo $IS_DEBUG


if [ "$IS_DEBUG" == "DEBUG" ]
then
    echo "Starting manage.py server"
    python manage.py runserver 0.0.0.0:8000
else
    echo "Starting gunicorn server"
    gunicorn --bind 0.0.0.0:8000 django_simple_web_course.wsgi
fi