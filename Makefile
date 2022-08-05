migrations:
	python manage.py makemigrations
migrate:
	python manage.py migrate
start:
	python manage.py runserver
server0:
	python manage.py runserver 0:8000
server:
	python manage.py runserver
build:
	python manage.py collectstatic
	python manage.py makemigrations
	python manage.py migrate
shell:
	python manage.py shell
static:
	python manage.py collectstatic
migratedb:
	python manage.py makemigrations
	python manage.py migrate
merge:
	python manage.py makemigrations --merge
margemigrate:
	python manage.py makemigrations --merge
	python manage.py migrate
