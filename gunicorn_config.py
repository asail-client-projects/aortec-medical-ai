import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 300
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# Process naming
proc_name = 'aortec_gunicorn'

# Server mechanics
daemon = False
pidfile = '/var/run/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# Preloading
preload_app = True

# StatsD (optional monitoring)
# statsd_host = 'localhost:8125'
# statsd_prefix = 'aortec'