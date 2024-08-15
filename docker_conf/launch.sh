#!/bin/bash
#
printenv > /home/django/app/docker_conf/envvariables.bak
IS_DEBUG=`/home/django/.env/bin/python /home/django/app/docker_conf/get_docker_env_var.py DEBUG_SERVER`
echo "Debug flag set to:"
echo "$IS_DEBUG"

MAX_RETRIES=30
RETRY_INTERVAL=5

# Wait for the database to become available
attempt=1
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    if [ $attempt -gt $MAX_RETRIES ]; then
        echo "Error: Database did not become available within the timeout period."
        exit 1
    fi

    echo "Waiting for the database to become available... Attempt $attempt"
    sleep $RETRY_INTERVAL
    ((attempt++))
done

echo "Database is now available."


echo "Applying migrations"
/home/django/.env/bin/python docker_conf/db_setup.py
/home/django/.env/bin/python django_simple_web_course/manage.py migrate --noinput
echo "Migrations applied"
echo "DB initialized"
echo "Collecting static files (this may take a moment)"
/home/django/.env/bin/python manage.py collectstatic --noinput
echo "Static files collected"   
ln -sf /home/django/app/staticfiles /var/www/static_root/static
service nginx start
[ -e /home/django/supervisor.sock ] && rm /home/django/supervisor.sock
supervisord
supervisorctl stop all
supervisorctl start all
echo "Supervisor started. Pause for 2 seconds logs to create so we can tail them"
sleep 2s
tail -f /var/log/django.out.log & tail -f /var/log/django.err.log
#tail -f /dev/null