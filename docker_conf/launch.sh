#!/bin/bash
service supervisor stop
service nginx stop
cp docker_conf/supervisor.conf /etc/supervisor/conf.d/local.supervisor.conf
cp docker_conf/nginx.conf /etc/nginx/sites-enabled/django_app.conf
mkdir -p /var/log/django_simple_web_course
[ -e /etc/nginx/sites-enabled/default ] && rm /etc/nginx/sites-enabled/default
printenv > /usr/src/app/docker_conf/envvariables.bak
python docker_conf/db_setup.py
echo "DB Setup Complete"
echo "Applying migrations"
python django_simple_web_course/manage.py migrate --noinput
echo "Migrations applied"
COLLECT_STATIC=`python /usr/src/app/docker_conf/get_docker_env_var.py COLLECT_STATIC`
if [ "$COLLECT_STATIC" == "True" ]
then
    echo "Collecting static files (this may take a moment)"
    python django_simple_web_course/manage.py collectstatic --noinput
    echo "Static files collected"
    mkdir -p /var/www/static_root
    ln -sf /usr/src/app/django_simple_web_course/static_root /var/www/static_root/static
fi
service supervisor start
service nginx start
echo "Supervisor started. Pause for 2 seconds logs to create so we can tail them"
sleep 2s
echo ""
echo ""
echo "Warning: Logs are being tailed. Old errors may show before new server lines"
echo ""
echo ""
echo ""
echo ""
tail -f /var/log/django_simple_web_course.out.log & tail -f /var/log/django_simple_web_course.err.log