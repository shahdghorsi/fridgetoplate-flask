# Gunicorn configuration file for FridgeToPlate application
# This file is used when deploying to Render

# Bind to 0.0.0.0:$PORT
bind = "0.0.0.0:$PORT"

# Worker configuration
workers = 2
threads = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "fridgetoplate"

# Server hooks
def on_starting(server):
    """
    Called just before the master process is initialized.
    """
    pass

def on_exit(server):
    """
    Called just before exiting.
    """
    pass
