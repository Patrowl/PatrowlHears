#!/bin/bash
export APP_HOST=${APP_HOST:-0.0.0.0}
export APP_PORT=${APP_PORT:-8303}
export POSTGRES_HOST=${POSTGRES_HOST:-db}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}
export RABBITMQ_HOST=${RABBITMQ_HOST:-rabbitmq}
export RABBITMQ_PORT=${RABBITMQ_PORT:-5672}
export SUPER_USERNAME=${SUPER_USERNAME:-admin}
export SUPER_PASSWORD=${SUPER_PASSWORD:-Bonjour1!}
export SUPER_EMAIL=${SUPER_EMAIL:-admin@hears.patrowl.io}
export SUPER_ORGNAME=${SUPER_ORGNAME:-Private}

echo "[+] Wait for DB availability"
while !</dev/tcp/$POSTGRES_HOST/$POSTGRES_PORT; do sleep 1; done

echo "[+] Wait for RabbitMQ availability"
while !</dev/tcp/$RABBITMQ_HOST/$RABBITMQ_PORT; do sleep 1; done

echo "[+] Activate python virtualenv"
cd backend_app
source env/bin/activate

# Collect static files
echo "[+] Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "[+] Make database migrations for User"
python manage.py makemigrations users

# Apply database migrations
echo "[+] Apply database migrations for User"
python manage.py migrate users

# Apply database migrations
echo "[+] Make database migrations"
python manage.py makemigrations

# Apply database migrations
echo "[+] Apply database migrations"
python manage.py migrate

# Create default admin user
echo "[+] Create default admin user if needed"
echo -e "from django.contrib.auth import get_user_model\r\
User = get_user_model()\r\
if not User.objects.filter(username='admin').exists():\r\
  User.objects.create_superuser('$SUPER_USERNAME', '$SUPER_EMAIL', '$SUPER_PASSWORD')" | python manage.py shell

echo "[+] Create default admin private organization if needed"
echo -e "\r\
from organizations.models import Organization, OrganizationUser, OrganizationOwner\r\
from django.contrib.auth import get_user_model\r\
admin_user = get_user_model().objects.get(username='$SUPER_USERNAME')\r\
if admin_user.organizations_organization.count() == 0:\r\
  admin_org = Organization.objects.create(name='$SUPER_ORGNAME', is_active=True)\r\
  admin_org.save()\r\
  org_user = OrganizationUser.objects.create(user=admin_user, organization=admin_org, is_admin=True)\r\
  org_user.save()\r\
  org_owner = OrganizationOwner.objects.create(organization=admin_org, organization_user=org_user)\r\
  org_owner.save()" | python manage.py shell

# Start Supervisord (Celery workers)
echo "[+] Start Supervisord (Celery workers)"
supervisord -c var/etc/supervisord.conf

# Start server
echo "[+] Starting server"
gunicorn -b $APP_HOST:$APP_PORT backend_app.wsgi:application --timeout 300
