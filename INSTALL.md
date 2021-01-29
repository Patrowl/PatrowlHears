# Installation notes for **PatrowlHears**

## Hardware Pre-requisites
PatrowlHears uses PosgreSQL to store data and RabbitMQ to process queues. We recommend using a virtual machine with at least 2vCPU, 8 GB of RAM and 50 GB of storage disk. You can also use a physical machine with similar specifications.

## Installation steps
### The very easy way: Use Docker
- Install Docker and Docker-compose
- Run the docker stack:
```
git clone https://github.com/Patrowl/PatrowlHears
cd PatrowlHears
docker-compose up
```
- Open your browser on http://localhost:8383
- Load initial DB records and latest updates:
```
docker-compose exec patrowlhears bash -c 'cd backend_app && ./load_init_data.sh'
docker-compose exec patrowlhears bash -c 'cd backend_app && ./import_data_updates.sh'
```
- Regularly update DB with command:
```
docker-compose exec patrowlhears bash -c 'cd backend_app && ./import_data_updates.sh'
```

### The easy way: Use installation script
- Install Python3 on your server
- Run the commands:
```
git clone https://github.com/Patrowl/PatrowlHears
cd PatrowlHears
./install.sh
```
- Open your browser on http://localhost:8383
- Regularly update DB with command:
```
cd backend_app && ./import_data_updates.sh
```

### The DevOps way: Install and deploy from Ansible playbook
- Go to the playbook location `cd deploy/ansible/playbooks`
- Copy and update the sample file `ansible/vars.yml.sample` to `ansible/vars.yml`
- Run the Ansible playbook:
```
ansible-playbook patrowlhears.yml -t patrowlhears-install -i myhost,
```
> Note 1: Do not forget to update Ansible vars and default ansible.cfg options.
> Note 2: Do not forget the comma ',' after the hostname/ip (well-known Ansible inventory trick).

### The Nerd way: Install and deploy from sources
The following section contains a step-by-step guide to build PatrowlHears from its sources.

#### 1. Install system pre-requisites
The following software are required to download and run PatrowlHears:
+ [PostgreSQL DB](https://www.postgresql.org/download/)
+ [Git client](http://www.git-scm.com/downloads)
+ [NPM](https://nodejs.org/en/download/)
+ [Python 3.7+](https://www.python.org/downloads)
+ [Python pip3](https://pip.pypa.io/en/stable/installing/)
+ [Python virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
+ [RabbitMQ](https://www.rabbitmq.com)
+ [Nginx](http://nginx.org/en/docs/)

We strongly recommend to use the system packages.
To install the requirements and run PatrowlHears from sources, please follow the instructions below depending on your operating system.

###### 1.1. MacOS/X with Brew
```
brew update
brew install postgres python3 rabbitmq npm
python -m ensurepip
pip install virtualenv
```

###### 1.2. Ubuntu 16.04/18.04/20.04 LTS with APT
```
sudo apt update
sudo apt upgrade -y
sudo apt install -y build-essential python3 python3-dev git curl rabbitmq-server postgresql postgresql-client nodejs libpq-dev nginx
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3 get-pip.py
rm get-pip.py
sudo pip3 install virtualenv
```

###### 1.3. CentOS/RHEL with YUM
```
sudo yum install -y git python3 python3-pip python3-virtualenv rabbitmq-server postgresql postgresql-client npm postgresql-devel
```

##### 2. Download PatrowlHears from GitHub
```
git clone https://github.com/Patrowl/PatrowlHears
```

##### 3. Build the frontend application (VueJS) - Optional
```
cd PatrowlHears/frontend
npm install
npm run build
```

##### 4. Install python dependencies within the virtualenv
```
cd ../backend_app
python3 -m virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
> Note 1: If `python3 -m virtualenv env` does not work, please consider the command `virtualenv env` but ensure that Python3 is selected.  
> Note 2: Be careful, next commands MUST be launched within the python3 virtual environment. The prefix `(env3)` should appear in the command prompt. Ex:
```
(env) GreenLock@GL02:PatrowlHears$ ls
```
If you opened another terminal, please ensure you use the virtualenv with the command `source env3/bin/activate`. If you want to exit the virtual environment, use the command `deactivate`. If not, do nothing and stop asking.
> Note 3: for MacOs users, install pythons modules from `requirements.macos.txt` file.

##### 5. Create the PostgreSQL database
+ Edit file the `var/db/create_user_and_db.sql` and update the user and password values (default values are: '`patrowlhears`' and '`patrowlhears`').
> Note: You should consider to set a strong password in Production.

###### 5.1. MacOS
+ Execute the SQL script:
```
psql < var/db/create_user_and_db.sql
```

###### 5.2. Ubuntu 16.04/18.04/20.04 LTS and CentOS/RHEL
+ Execute the SQL script:
```
sudo -u postgres psql < var/db/create_user_and_db.sql
```
> Note: By default, the script create the database 'patrowlhears_db' with the user/role 'patrowlhears'. The default password is 'patrowlhears'. If you change these settings, do not forget to update the `backend_app/settings.py` configuration file with your updates, or pass it it using environment variables.

##### 6. Configure PatrowlHears (Django backend) application
+ Copy `backend_app/settings.py.sample` to `backend_app/settings.py` and update at least following options:
  * Application settings `ALLOWED_HOSTS`, `LOGGING_LEVEL`, `PROXIES`, `SECRET_KEY`
  * DB settings (service location and credentials): `DATABASES`,  
  * RabbitMQ settings (service location and credentials): `BROKER_URL` (default values are `guest/guest`),
  * Email settings (alerting): `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_HOST_PORT`
+ Create the db schema using the Django commands:
```
python manage.py makemigrations
python manage.py migrate
```

+ Collect static files (production mode - all static files copied to /staticfiles/ and will be served by NGinx):
```
python manage.py collectstatic --noinput
```

+ Create the Django superuser with all privileges, more than Batman but without a cape:
```
python manage.py shell < var/bin/create_default_admin.py
```
> Note 1: Default login is `admin` and password is `Bonjour1!`.\
> Note 2: You are in charge to renew the password once the application started. Please keep these credentials in a safe place. This account will be used for the first login on the PatrowlHears application.

+ Create the default organization:
```
python manage.py shell < var/bin/create_default_organization.py
```

##### 7. Start the Django backend server
###### 7.1 Testing environment
+ Start Supervisord (Celery workers consuming the tasks enqueued RabbitMQ - Yes, that's how asynchronus tasks work here):
```
supervisord -c var/etc/supervisord.conf
```
> Note: The Supervisor daemon will be listening on port TCP/9002. Update this in the configuration file if you are not agree with that arbitrary choice. Who really cares ?

+ Check every celery workers are in state `RUNNING`:
```
supervisorctl -s http://127.0.0.1:9002 status all
```
+ Then, the Django application (development only):
```
python manage.py runserver 127.0.0.1:8000
```
+ or, using Gunicorn (recommended in production):
```
gunicorn backend_app.wsgi:application -b 127.0.0.1:8000 --access-logfile -
```

###### 7.2 Production environment (Nginx serving static files)
+ Open the `backend_app/settings.py` file and set the variable `DEBUG=False`.
+ Follow the same steps for starting the development environment (see #7.1)
+ Customize the `nginx.conf` file provided. Then start it:
```
[sudo] nginx -p .
```
> Note: By default the WEB pages is exposed from port TCP/8383

##### 8. Load initial DB fixtures and latest updates
- Run following commands (in path `backend_app`):
```
./load_init_data.sh
./import_data_updates.sh
```

###### Need help ? Stuck somewhere ?
Don't panic! The community could help you as soon as you double-checked your issue and its undoubtedly related to PatrowlHears installation:
+ Contact us at `getsupport@patrowl.io`, or
+ Chat with us on [Gitter](https://gitter.im/PatrowlHears/Support)


Follow us [@patrowl_io](https://twitter.com/patrowl_io)
