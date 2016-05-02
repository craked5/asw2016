import os

bind = '0.0.0.0:8000'
workers = 1
backlog = 2048
worker_class = "sync"
daemon = True
debug = True
proc_name = 'gunicorn.proc'
pidfile = '/tmp/gunicorn.pid'
logfile = '/root/gunicorn/debug.log'
loglevel = 'debug'