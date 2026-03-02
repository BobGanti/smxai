# gunicorn.conf.py
import os

# Respect Cloud Run's PORT
bind = f":{os.environ.get('PORT', '8080')}"

# Stable concurrency for Cloud Run
workers = 1          # avoid fork storms / keeps memory stable
threads = 4          # lightweight concurrency
worker_class = "gthread"

# Timeouts (fixes the admin page/LLM timeouts you saw)
timeout = 300            # hard timeout
graceful_timeout = 60
keepalive = 120

# Sensible logging to stdout/stderr
accesslog = "-"
errorlog  = "-"
loglevel  = "info"

