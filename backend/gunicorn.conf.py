# gunicorn.conf.py
bind = "127.0.0.1:9096"
workers = 3
timeout = 120
worker_class = "sync"

# 日志配置
accesslog = "/var/log/gunicorn/access-digit.log"
errorlog = "/var/log/gunicorn/error-digit.log"
loglevel = "info"

# 可选：将 stdout/stderr 重定向到 errorlog
capture_output = True

# 可选：打印进程 PID
pidfile = "/var/run/gunicorn.pid"