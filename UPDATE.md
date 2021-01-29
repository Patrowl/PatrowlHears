# Updates notes for **PatrowlHears**

## Docker
```
cd PatrowlHears
git pull
docker build .
docker-compose down
docker-compose up --force-recreate
```

## Native installation
```
cd PatrowlHears
git pull
cd backend_app
source env/bin/activate
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
supervisorctl -s http://localhost:9002 restart all
supervisord -c var/etc/supervisord.conf
sleep 3
supervisorctl -s http://localhost:9002 status
gunicorn -b 0.0.0.0:8083 backend_app.wsgi:application --timeout 300
sudo nginx -s reload
deactivate
```

###### Need help ? Stuck somewhere ?
Don't panic! The community could help you as soon as you double-checked your issue and its undoubtedly related to PatrowlHears installation:
+ Contact us at `getsupport@patrowl.io`, or
+ Chat with us on [Gitter](https://gitter.im/PatrowlHears/Support)
