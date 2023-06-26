.PHONY: build run init-records update-records update-records-pro

build:
	docker-compose build --no-cache

run: 
	docker-compose up --remove-orphans

init-records:
	docker-compose exec patrowlhears bash -c 'cd backend_app && ./load_init_data.sh'

update-records:
	docker-compose exec patrowlhears bash -c 'cd backend_app && ./import_data_updates.sh'

update-records-pro:
	docker-compose exec patrowlhears bash -c 'cd backend_app && env/bin/python manage.py downloadfeeds -o /tmp'
	docker-compose exec patrowlhears bash -c 'cd backend_app && env/bin/python manage.py importfeeds_vulns -d /tmp/PatrowlHearsFeeds/feeds/'
	docker-compose exec patrowlhears bash -c 'cd backend_app && env/bin/python manage.py importfeeds_exploits -d /tmp/PatrowlHearsFeeds/feeds/'