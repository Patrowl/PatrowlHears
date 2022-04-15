#!/bin/bash
export APP_HOST=${APP_HOST:-127.0.0.1}
export APP_PORT=${APP_PORT:-8303}
export WEB_PORT=${WEB_PORT:-8383}
export WEB_BASE_DOMAIN=${WEB_BASE_DOMAIN:-hears.patrowl.io}
export DB_PORT_5432_TCP_HOST=${DB_PORT_5432_TCP_HOST:-localhost}
export DB_PORT=${DB_PORT:-5432}
export RABBITMQ_HOST=${RABBITMQ_HOST:-localhost}
export RABBITMQ_PORT=${RABBITMQ_PORT:-5672}
export MEMCACHED_HOST=${MEMCACHED_HOST:-memcached}
export MEMCACHED_PORT=${MEMCACHED_PORT:-11211}
export SUPER_USERNAME=${SUPER_USERNAME:-admin}
export SUPER_PASSWORD=${SUPER_PASSWORD:-Bonjour1!}
export SUPER_EMAIL=${SUPER_EMAIL:-admin@mockpatrowlhears.io}
export SUPER_ORGNAME=${SUPER_ORGNAME:-Private}

python3 -mplatform | grep -qiE 'Ubuntu|Linux' && {
  sudo apt update
  sudo apt upgrade -y
  sudo apt install -y -f build-essential python3 python3-dev git curl rabbitmq-server postgresql postgresql-client nodejs libpq-dev nginx memcached libmemcached-tools
  sudo systemctl restart nginx
  sudo systemctl start postgresql.service
  sudo systemctl enable postgresql.service
  sudo systemctl restart memcached
  sudo systemctl enable memcached
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  sudo python3 get-pip.py
  rm get-pip.py
  sudo pip3 install virtualenv
}
python3 -mplatform | grep -qi centos && {
  sudo yum upgrade
  sudo yum install -y git python3 python3-pip python3-virtualenv rabbitmq-server postgresql postgresql-client nodejs postgresql-devel nginx memcached libmemcached
  sudo systemctl start nginx
  sudo systemctl start memcached
  sudo systemctl enable memcached
}
python3 -mplatform | grep -qi macOS && {
  brew update
  brew install postgres python3 rabbitmq nginx memcached
  brew services start postgres
  brew services start rabbitmq
  brew services start nginx
  brew services start memcached
  python -m ensurepip
  pip install virtualenv
}

echo "[+] Wait for DB availability"
while !</dev/tcp/$DB_PORT_5432_TCP_HOST/$DB_PORT; do sleep 1; done

echo "[+] Wait for RabbitMQ availability"
while !</dev/tcp/$RABBITMQ_HOST/$RABBITMQ_PORT; do sleep 1; done

echo "[+] Wait for Memcached availability"
while !</dev/tcp/$MEMCACHED_HOST/$MEMCACHED_PORT; do sleep 1; done

echo "[+] Go to backend dir"
cd backend_app

echo "[+] Create DB"
python3 -mplatform | grep -qi macOS && {
  psql < var/db/create_user_and_db.sql
}
python3 -mplatform | grep -qiE 'centos|Ubuntu|Linux' && {
  sudo -u postgres psql < var/db/create_user_and_db.sql
}

echo "[+] Copy settings from template if not exists"
[ -f backend_app/settings.py ] || cp backend_app/settings.py.sample backend_app/settings.py

echo "[+] Activate python virtualenv"
virtualenv env --python=python3
source env/bin/activate
pip install -r requirements.txt

# Collect static files
echo "[+] Collect static files"
python manage.py collectstatic --noinput

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
echo "[+] (Re-)Start Supervisord (Celery workers)"
supervisorctl -s http://127.0.0.1:9002 shutdown
sleep 5
supervisord -c var/etc/supervisord.conf
sleep 3
supervisorctl -s http://127.0.0.1:9002 status all

# Start backend server
echo "[+] Starting backend server (Gunicorn) on $APP_HOST:$APP_PORT"
gunicorn -b $APP_HOST:$APP_PORT backend_app.wsgi:application --timeout 300 --workers 2 --daemon

# Start WEB server
echo "[+] Starting WEB server (nginx) on $APP_HOST:$WEB_PORT"
python3 -mplatform | grep -qi macOS && {
  sudo cp var/etc/nginx.conf.tpl /usr/local/etc/nginx/sites-enabled/patrowlhears.conf
  sudo sed -i "s|__PH_INSTALL_DIR__|`pwd`|g" /usr/local/etc/nginx/sites-enabled/patrowlhears.conf
  sudo sed -i "s|__PH_BASE_DOMAIN__|$WEB_BASE_DOMAIN|g" /usr/local/etc/nginx/sites-enabled/patrowlhears.conf
}
python3 -mplatform | grep -qiE 'centos|Ubuntu|Linux' && {
  sudo cp var/etc/nginx.conf.tpl /etc/nginx/sites-enabled/patrowlhears.conf
  sudo sed -i "s|__PH_INSTALL_DIR__|`pwd`|g" /etc/nginx/sites-enabled/patrowlhears.conf
  sudo sed -i "s|__PH_BASE_DOMAIN__|$WEB_BASE_DOMAIN|g" /etc/nginx/sites-enabled/patrowlhears.conf
}
sudo nginx -s reload

echo "[+] Load initial DB data"
./load_init_data.sh

echo "[+] Fetch and load latest DB updates from public repos"
./import_data_updates.sh

echo "[+] Installation finished."
echo "[!] Visit https://patrowlhears.io"
echo "[?] Contact us at getsupport@patrowl.io, or chat with us on Gitter: https://gitter.im/PatrowlHears/Support"
