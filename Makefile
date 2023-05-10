SHELL := /bin/bash

env-setup:
	rm -rf venv
	python3.8 -m venv venv; \
	source venv/bin/activate; \
	pip install -r requirements.txt



run-local:
	source venv/bin/activate; \
	export CONFIG_PATH=common/configs/local.cfg; \
	python manage.py makemigrations; \
	python manage.py migrate; \
	black .; \
	python manage.py runserver

run-dev:
	conda deactivate; \
	conda activate user; \
	pip install -r requirements.txt; \
	export CONFIG_PATH=common/configs/dev.cfg; \
	python manage.py makemigrations; \
	python manage.py migrate; \
	rm -rf src/static; \
	python manage.py collectstatic; \
	sudo systemctl restart user

run-user:
	source venv/bin/activate; \
	black .; \
	export CONFIG_PATH=common/configs/users/$(USER).cfg; \
	python manage.py makemigrations; \
	python manage.py migrate; \
	python manage.py runserver 8081

run-grpc-local:
	source venv/bin/activate
	export CONFIG_PATH=common/configs/local.cfg; \
	python grpc_server.py

run-grpc-dev:
	source venv/bin/activate
	export CONFIG_PATH=common/configs/dev.cfg; \
	python grpc_server.py

run-grpc-user:
	source venv/bin/activate; \
	export CONFIG_PATH=common/configs/users/$(USER).cfg; \
	export DJANGO_SETTINGS_MODULE=src.settings; \
	python grpc_server.py

celery:
	source venv/bin/activate; \
	export CONFIG_PATH=common/configs/users/$(USER).cfg; \
	python -m celery -A celery_server worker -l info  -Q user-service-queue