manage.py = homework5/manage.py
main_app = homework5

fill_posts:
	python $(manage.py) fill_posts

install:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

shell: # only after 'make extensions-install'
	python $(manage.py) shell_plus --print-sql

run:
	python $(manage.py) runserver

kill-port:
	sudo fuser -k 8000/tcp

migrate:
	python $(manage.py) makemigrations
	python $(manage.py) migrate

check:
	python $(manage.py) check

migrations-dry:
	python $(manage.py) makemigrations --dry-run

gen-book-category:
	python $(manage.py) gen_book_category

flake8-install:
	pip install flake8
	pip install flake8-import-order # сортировку импортов
	pip install flake8-docstrings # доки есть и правильно оформлены
	pip install flake8-builtins # что в коде проекта нет переменных с именем из списка встроенных имён
	pip install flake8-quotes # проверять кавычки

	# ставим гит-хук
	flake8 --install-hook git
	git config --bool flake8.strict true

debugger-install:
	python -m pip install django-debug-toolbar
	# 'debug_toolbar'                                    | add to the INSTALLED_APPS in settings.py
	# debug_toolbar.middleware.DebugToolbarMiddleware    | add to the MIDDLEWARE in settings.py
	# INTERNAL_IPS = [ "127.0.0.1", ]					 | create in the settings.py
	# path('__debug__/', include(debug_toolbar.urls))    | add to the urls.py in project DIR
	# import debug_toolbar                               | add to the urls.py in project DIR

extensions-install:
	python pip install django-extensions
	python pip install ipython
	# 'django_extensions'                                | add to the INSTALLED_APPS in settings.py

#  Celery
#
#
celery:
	python pip install -U Celery
#	ubuntu: sudo apt-get install -y erlang
#			sudo apt-get install rabbitmq-server
#			systemctl enable rabbitmq-server
#			systemctl start rabbitmq-server
#			systemctl status rabbitmq-server
#
#	settings.py:
#			CELERY_BROKEN_URL = 'amqp://localhost'
#	celery.py:
#			import os
#			from celery import Celery
#
#			os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
#
#			app = Celery('mysite')
#			app.config_from_object('django.conf:settings', namespace='CELERY')
#			app.autodiscover_tasks()
#	__init__.py:
#  			from .celery import app as celery_app
#
#			__all__ = ['celery_app']
#

worker:
	cd $(main_app) && celery -A $(main_app) worker --autoscale=4,2 -l info

beat:
	cd $(main_app)/&& celery -A $(main_app) beat -l info

worker-info:
	cd $(main_app) && celery -A $(main_app) events

# worker-info-web:
#	in basic console:
#   pip install flower
#   source venv/bin/activate
#	cd *my_proj*
#	celery -A *my_proj* flower

#	ps aux | grep celery
#   pkill -f csp_build.py   its a grep based kill

# signals
#
#
#
#
#        error_messages = {
#            NON_FIELD_ERRORS: {
#                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
#            },
#            'email_to': {
#                'required': "Email field is empty.",
#                'invalid': "Enter a valid email address.",
#            },
#        }
