web: PYTHONPATH=finalproject/PROJECT111/backend gunicorn finalproject.PROJECT111.backend.config.wsgi:application
worker: PYTHONPATH=finalproject/PROJECT111/backend celery -A config worker -l info -c 1