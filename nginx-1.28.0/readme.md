```
sudo -u postgres psql
```

```
psql -h 127.0.0.1 -U vue3_comany
```



```
-- 1. 确保数据库归属
ALTER DATABASE vue3_comany OWNER TO vue3_comany;

-- 2. 授予 schema 权限（关键！）
GRANT CREATE ON SCHEMA public TO vue3_comany;
GRANT USAGE ON SCHEMA public TO vue3_comany;

-- 3. （可选）设置默认权限，避免未来问题
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO vue3_comany;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO vue3_comany;
```

```
psql -U vue3_comany -d vue3_comany -h localhost -W
```



##### 开机启动服务

```
/etc/systemd/system/digit-platform.service
```

```
[Unit]
Description=Gunicorn for digit-platform
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/www/yue/digit-platform/backend
ExecStart=/root/anaconda3/envs/py38digit/bin/gunicorn --bind 127.0.0.1:9096 --workers 3 --timeout 120 backend.wsgi:application
Restart=on-failure
RestartSec=10

# 日志重定向（备用）
StandardOutput=append:/var/log/gunicorn/out-digit-platform.log
StandardError=append:/var/log/gunicorn/err-digit-platform.log
```



##### 开机自启动命令

```
sudo systemctl daemon-reload
sudo systemctl enable digit-platform
sudo systemctl start digit-platform
sudo systemctl status digit-platform
```

