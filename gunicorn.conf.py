# gunicorn.conf.py
worker_class = "sync"
workers = 2           # 1 might be okay; try 2 if memory allows
threads = 2
timeout = 120         # you had 120 — ok
keepalive = 5
max_requests = 50
max_requests_jitter = 10

# Logging
capture_output = True
loglevel = "info"
accesslog = "-"
errorlog = "-"
