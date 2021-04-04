web: gunicorn --workers=2 --log-level=debug app:app
worker: python worker.py
keep_alive: python services/keep_alive_service.py