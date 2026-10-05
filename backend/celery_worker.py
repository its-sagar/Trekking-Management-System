"""Celery worker entry point. Run with:
   celery -A celery_worker.celery_app worker --loglevel=info
   In windows(For CMD: set PYTHONPATH="." , POWERSHELL: $env:PYTHONPATH=".")
   celery -A celery_worker.celery_app worker --loglevel=info -P solo
   celery -A celery_worker.celery_app beat --loglevel=info
"""
from tasks import celery_app

if __name__ == '__main__':
    celery_app.start()
