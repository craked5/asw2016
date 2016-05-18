import os

bind = '0.0.0.0:8081'
workers = 1
backlog = 2048
worker_class = "eventlet"
daemon = True
debug = True
proc_name = 'gunicorn.proc'
pidfile = '/tmp/gunicorn.pid'
logfile = '/root/gunicorn/debug.log'
loglevel = 'debug'