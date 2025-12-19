# 视频素材创作管理系统



## 技术架构

### 后端技术栈

- Python3.8
- Django
- Celery
- Restframework
- PostgreSQL
- ...

### 前端技术栈

- Vue3
- Element-Plus
- TypeScript
- Echarts
- CryptoJS & CryptoSM 
- ...

### 界面预览

![1766108802753](images\1766108802753.png)

![1766108831425](images\1766108831425.png)

![1766108910008](images\1766108910008.png)

![1766108967226](images\1766108967226.png)

![1766109062766](images\1766109062766.png)

![1766109088623](images\1766109088623.png)





## API 文档

### 认证

- `POST /api/token/` - 获取JWT令牌 (username, password)
- `POST /api/token/refresh/` - 刷新JWT令牌
- `POST /api/token/verify/` - 验证JWT令牌

### 用户管理

- `GET /api/users/` - 获取用户列表
- `POST /api/users/` - 创建用户
- `GET /api/users/{id}/` - 获取用户详情
- `PUT /api/users/{id}/` - 更新用户
- `PATCH /api/users/{id}/` - 部分更新用户
- `DELETE /api/users/{id}/` - 删除用户
- `GET /api/users/current_user/` - 获取当前用户信息
- `PUT /api/users/{id}/change_status/` - 更改用户状态

### 部门管理

- `GET /api/departments/` - 获取部门列表
- `POST /api/departments/` - 创建部门
- `GET /api/departments/{id}/` - 获取部门详情
- `PUT /api/departments/{id}/` - 更新部门
- `PATCH /api/departments/{id}/` - 部分更新部门
- `DELETE /api/departments/{id}/` - 删除部门

### 角色管理

- `GET /api/roles/` - 获取角色列表
- `POST /api/roles/` - 创建角色
- `GET /api/roles/{id}/` - 获取角色详情
- `PUT /api/roles/{id}/` - 更新角色
- `PATCH /api/roles/{id}/` - 部分更新角色
- `DELETE /api/roles/{id}/` - 删除角色

### 菜单管理

- `GET /api/menus/` - 获取菜单列表
- `POST /api/menus/` - 创建菜单
- `GET /api/menus/{id}/` - 获取菜单详情
- `PUT /api/menus/{id}/` - 更新菜单
- `PATCH /api/menus/{id}/` - 部分更新菜单
- `DELETE /api/menus/{id}/` - 删除菜单
- `GET /api/menus/tree/` - 获取菜单树

### 素材管理

- `POST  /file/api/files/query/?page=1&page_size=10 ` - 获取素材列表
- `POST /file/api/upload/init/` - 素材上传初始化
- `POST  /file/api/upload/chunk/ `- 素材分片上传
- `POST  /file/api/upload/complete/ `- 素材上传完成
- `POST  /file/api/download/{id}/download-start/ `- 素材下载开始
- `GET  /file/api/download/{id}/download/` - 素材断点续传下载
- `POST /file/api/download/{id}/download-complete/ `- 素材下载完成
- `PUT /file/api/files/{id}/edit/` - 编辑素材
- `PATCH /file/api/files/{id}/rename/` - 更新素材名称
- `DELETE  /file/api/files/{id}/delete/ ` - 删除素材



### PostgreSQL授权用户

以管理员身份进入数据库

```
psql -h 127.0.0.1 -U postgres -d postgres

-- 授予 vue3_comany 用户所有权限
GRANT ALL PRIVILEGES ON DATABASE vue3_comany TO vue3_comany;
GRANT ALL PRIVILEGES ON SCHEMA public TO vue3_comany;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vue3_comany;


```

```
-- 授予数据库所有权（如果数据库已存在）
ALTER DATABASE vue3_comany OWNER TO vue3_comany;

-- 授予 schema public 的所有权限
GRANT ALL PRIVILEGES ON SCHEMA public TO vue3_comany;

-- 授予已存在表的所有权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vue3_comany;

-- 授予未来新建表的所有权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vue3_comany;

-- 授予序列权限（Django 需要）
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vue3_comany;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO vue3_comany;

-- 直接让用户成为超级用户：
ALTER USER vue3_comany WITH SUPERUSER;
```



### sqlite数据迁移到postgresql

##### 1：导出数据

```
# 导出数据

python manage.py dumpdata --output datadump.json --format json --indent 2

```

##### 2：电脑上记事本打开datadump.json另存编码格式选择utf-8

##### 3: 使用 Python 删除 BOM 并保存为无 BOM 的 UTF-8 文件（推荐）

 创建一个 Python 脚本，比如 `remove_bom.py`： 

```
# remove_bom.py

import sys

input_file = 'datadump_utf8.json'
output_file = 'datadump_utf8_nobom.json'

with open(input_file, 'r', encoding='utf-8-sig') as f_in:
    content = f_in.read()

with open(output_file, 'w', encoding='utf-8') as f_out:
    f_out.write(content)

print("✅ 成功移除 BOM，已保存为无 BOM 的 UTF-8 文件")
```



##### 4：清除现有数据重新导入（导入移除BOM后的datadump_utf8_nobom.json文件）

```
# 1. 清空数据库表（谨慎操作！）
python manage.py flush --noinput

# 2. 重新创建表结构
python manage.py migrate

# 3. 重新导入数据 --exclude 参数，排除系统表或冲突的表
python manage.py loaddata datadump_utf8_nobom.json --exclude=contenttypes.ContentType --exclude=user.Profile
```





### celery部署



### **1. 基础检查**

#### (1) 确保服务已正确启动



```
# 查看Celery进程是否存活
ps aux | grep celery

# 检查Redis连接
redis-cli ping  # 应返回 "PONG"
```

#### (2) 验证任务注册



```
celery -A backend inspect registered
```

正常应显示您定义的任务（如 `vpn.tasks.monitor_vpn_task`）

------

### **2. 关键配置检查**

#### (1) `settings.py` 必须包含



```
# 确保时区配置正确
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

# Celery配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_TIMEZONE = 'Asia/Shanghai'
```

#### (2) 任务文件规范检查

确保 `vpn/tasks.py` 正确定义：



```
from celery import shared_task

@shared_task(bind=True)
def monitor_vpn_task(self):
    # 任务逻辑
    print("Task executed!")
```

------

### **3. 启动命令优化**

#### (1) 开发环境测试命令



```
# 前台启动（显示实时日志）
celery -A backend worker --loglevel=DEBUG -P solo
```

#### (2) 生产环境完整命令



```
celery -A backend worker --loglevel=INFO \
  --concurrency=4 \
  --uid=celeryuser \
  --pidfile=/var/run/celery/worker.pid \
  --logfile=/var/log/celery/worker.log
```

------

### **4. 定时任务专用配置**

#### (1) 启动Beat服务



```
celery -A backend beat \
  --scheduler django_celery_beat.schedulers:DatabaseScheduler \
  --loglevel=DEBUG
```

#### (2) 通过Admin创建定时任务

1. 访问 `/admin/django_celery_beat/periodictask/`
2. 创建新任务：
   - Task: `vpn.tasks.monitor_vpn_task`
   - Schedule: 选择间隔（如每5分钟）
   - Enabled: 勾选

------

### **5. 权限与日志排查**

#### (1) 检查文件权限



```
sudo chown -R celeryuser:celeryuser /var/log/celery/
sudo chmod -R 775 /var/log/celery/
```

#### (2) 查看关键日志



```
# Celery日志
tail -f /var/log/celery/worker.log

# Redis日志
journalctl -u redis -f

# 系统日志
journalctl -xe
```

------

### **6. 常见问题解决方案**

#### (1) 任务未注册

**现象**：`inspect registered` 无输出
**解决**：

```
# 确保项目__init__.py初始化Celery
from .celery import app as celery_app
__all__ = ('celery_app',)
```

#### (2) 时区问题

**现象**：任务计划时间不对
**解决**：



```
timedatectl set-timezone Asia/Shanghai
sudo systemctl restart celery-beat
```

#### (3) 数据库表未迁移



```
python manage.py migrate django_celery_beat
```

------

### **7. 完整部署示例**

#### (1) systemd服务文件

`/etc/systemd/system/celery.service`：

ini

```
[Unit]
Description=Celery Service
After=redis.target

[Service]
User=celeryuser
Group=celeryuser
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A backend worker --loglevel=INFO --concurrency=4
Restart=always
RestartSec=10
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

#### (2) 启动服务

bash

```
sudo systemctl daemon-reload
sudo systemctl enable celery
sudo systemctl start celery
```

------

### **验证任务执行**

1. **手动触发测试**：

   

   ```
   python manage.py shell
   ```

   

   ```
   from vpn.tasks import monitor_vpn_task
   monitor_vpn_task.delay()  # 检查worker是否处理
   ```

2. **监控队列**：

   

   ```
   redis-cli monitor | grep celery
   ```

3. **可视化监控（可选）**：

   

   ```
   pip install flower
   celery -A backend flower --port=5555
   ```

   访问 `http://服务器IP:5555`

------

按照以上步骤系统排查后，95%的Celery任务不执行问题都能解决。如果仍有问题，请提供：

1. `celery -A backend inspect registered` 输出
2. `/var/log/celery/worker.log` 最新错误片段
3. 您的任务函数完整代码





##  Supervisor 配置示例，

##### 适用于使用 Django 的项目中管理 Celery Worker 和 Beat 

##### 使用兼容 Python 3 的 fork 版本（适用于需要 pip 安装的情况）

你可以使用社区维护的、兼容 Python 3 的 `supervisor` 分支：

```
pip install git+https://github.com/Supervisor/supervisor 
```



```
supervisord --version
# 应该输出类似：4.2.0 或更高（具体取决于当前 master 分支的版本）
```

 如果你看到版本号，说明 Supervisor 成功安装了！ 



## 🛠️ 配置 Supervisor 管理 Celery Worker 和 Beat

下面是一个完整的配置示例，适用于你的项目结构。请根据你的实际情况修改路径和名称。

------

### 1. 创建 Supervisor 配置文件目录（如未存在）

```
sudo mkdir -p /etc/supervisor/conf.d
```



------

### 2. 编辑主配置文件（如未存在）

```
sudo nano /etc/supervisor/supervisord.conf
```

添加以下内容：

```
[unix_http_server]
file=/var/run/supervisor.sock   ; (the path to the socket file)
chmod=0700                       ; sockef file mode (default 0700)

[supervisord]
logfile=/var/log/supervisor/supervisord.log ; main log file
pidfile=/var/run/supervisord.pid ; supervisord pidfile
childlogdir=/var/log/supervisor

;RPC 接口设置
[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock ; use a unix process socket

; 包含所有 conf.d 下的配置
[include]
files = /etc/supervisor/conf.d/*.conf
```



------

### 3. 创建 Celery Worker 配置文件

```
sudo nano /etc/supervisor/conf.d/celery-worker.conf
```

内容如下（请替换 `your_project`, `/path/to/your/project`, `/path/to/venv`）：

```
[program:celery-worker]
command=/path/to/venv/bin/celery -A your_project worker --loglevel=info
directory=/path/to/your/project
user=your_user
environment=PATH="/path/to/venv/bin",DJANGO_SETTINGS_MODULE="your_project.settings"
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/celery-worker.log
stderr_logfile=/var/log/celery-worker-err.log
numprocs=1
process_name=%(program_name)s-%(process_num)02d
```



------

### 4. 创建 Celery Beat 配置文件

```
sudo nano /etc/supervisor/conf.d/celery-beat.conf
```

内容如下：

```
[program:celery-beat]
command=/path/to/venv/bin/celery -A your_project beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info
directory=/path/to/your/project
user=your_user
environment=PATH="/path/to/venv/bin",DJANGO_SETTINGS_MODULE="your_project.settings"
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery-beat.log
stderr_logfile=/var/log/celery-beat-err.log
```



------

### 5. 创建日志目录并授权

```
sudo mkdir -p /var/log/supervisor /var/log/celery
sudo chown -R your_user:your_user /var/log/supervisor /var/log/celery
```



------

## 🔁 启动 Supervisor 并加载配置

```
sudo supervisord -c /etc/supervisor/supervisord.conf
```

如果报错权限问题，也可以用 root 用户运行：

```
sudo -i

supervisord -c /etc/supervisor/supervisord.conf
```



------

## 📋 查看状态 & 控制服务

```
sudo supervisorctl status

sudo supervisorctl stop celery-worker

sudo supervisorctl start celery-worker

sudo supervisorctl restart celery-worker
```



------

## 🧼 设置开机启动（systemd 示例）

创建 systemd 服务：

```
sudo nano /etc/systemd/system/supervisor.service
```

写入以下内容（根据你的环境调整路径）：

```
[Unit]
Description=Supervisor process control system for UNIX
Documentation=http://supervisord.org
After=network.target

[Service]
ExecStart=/usr/local/bin/supervisord -n -c /etc/supervisor/supervisord.conf
ExecStop=/usr/local/bin/supervisorctl $OPTIONS shutdown
ExecReload=/usr/local/bin/supervisorctl $OPTIONS reload
KillMode=mixed
Restart=on-failure
User=root

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```
sudo systemctl enable supervisor

sudo systemctl start supervisor
```



------

## ✅ 总结

| 操作            | 命令                                                       |
| --------------- | ---------------------------------------------------------- |
| 安装 Supervisor | `pip install git+https://github.com/Supervisor/supervisor` |
| 创建配置文件    | `/etc/supervisor/supervisord.conf`+`conf.d/*.conf`         |
| 启动 Supervisor | `supervisord -c /etc/supervisor/supervisord.conf`          |
| 管理进程        | `supervisorctl`                                            |
| 开机自启        | 使用 systemd                                               |









# 分析Nginx配置导致静态文件404的原因

您的Nginx配置有几个问题可能导致静态文件返回404错误。以下是详细分析和解决方案：

## 主要问题

1. **根目录(root)设置冲突**：
   ```nginx
   root /www/yue/vue-django-project/vue3-company/backend/media;
   ```
   这个设置会影响所有未明确指定`alias`的location块，可能导致路径解析错误。

2. **静态文件路径重复定义**：
   - 您的配置中有多个地方处理静态文件，可能导致冲突
   - 特别是通用静态文件处理规则和特定`/static/`规则可能冲突

3. **路径结尾斜杠问题**：
   - `alias`指令对结尾斜杠非常敏感
   - 确保Django的`STATIC_URL`和Nginx的`location`匹配

## 解决方案

### 1. 修改根目录设置

将根目录设置改为更通用的路径或完全移除（因为您已经为每个location指定了alias）：

```nginx
server {
    listen 80;
    server_name vpn.newdmy.com;
    # 移除或修改root指令
    root /www/yue/vue-django-project/vue3-company/backend;
    ...
}
```

### 2. 修正静态文件配置

简化并修正静态文件配置：

```nginx
# 静态文件配置 - 替换原有配置
location /static/ {
    alias /www/yue/vue-django-project/vue3-company/backend/static/;
    expires 365d;
    access_log off;
    add_header Cache-Control "public, max-age=31536000, immutable";
    
    # 确保目录存在且可读
    if (!-e $request_filename) {
        return 404;
    }
}

# 媒体文件配置 - 保持不变
location /media/ {
    alias /www/yue/vue-django-project/vue3-company/backend/media/;
    expires 30d;
    access_log off;
}
```

### 3. 移除冲突的静态文件处理规则

删除以下重复的静态文件处理规则：
```nginx
location ~ .*\.(gif|jpg|jpeg|png|bmp|swf)$
location ~ .*\.(js|css)?$
location ~* \.(jpg|jpeg|png|gif|ico|css|js|pdf|woff|woff2|ttf|svg|eot|pdf)$
```

### 4. 验证路径

确保以下路径确实存在且包含静态文件：
```bash
ls -la /www/yue/vue-django-project/vue3-company/backend/static/
```

### 5. 检查Django配置

确保Django的`settings.py`中有：
```python
STATIC_URL = '/static/'
STATIC_ROOT = '/www/yue/vue-django-project/vue3-company/backend/static/'
```

并运行：
```bash
python manage.py collectstatic
```

### 6. 测试和重载Nginx

```bash
# 测试配置
nginx -t

# 重载配置
systemctl reload nginx
```

## 完整修正后的配置建议

```nginx
server {
    listen 80;
    server_name vpn.newdmy.com;
    root /www/yue/vue-django-project/vue3-company/backend;
    
    access_log /www/wwwlogs/vpn.newdmy.com.log;
    error_log /www/wwwlogs/vpn.newdmy.com.error.log;

    # 静态文件配置
    location /static/ {
        alias /www/yue/vue-django-project/vue3-company/backend/static/;
        expires 365d;
        access_log off;
        add_header Cache-Control "public, max-age=31536000, immutable";
        
        # 文件类型设置
        types {
            text/css css;
            application/javascript js;
            image/svg+xml svg;
            image/png png;
            image/jpeg jpg jpeg;
            font/woff2 woff2;
        }
    }

    # 媒体文件配置
    location /media/ {
        alias /www/yue/vue-django-project/vue3-company/backend/media/;
        expires 30d;
        access_log off;
    }

    # 其他原有配置保持不变...
}
```

## 验证步骤

1. 访问静态文件URL，检查是否仍然404
2. 检查Nginx错误日志：
   ```bash
   tail -f /www/wwwlogs/vpn.newdmy.com.error.log
   ```
3. 确认文件权限：
   ```bash
   chown -R www:www /www/yue/vue-django-project/vue3-company/backend/static/
   chmod -R 755 /www/yue/vue-django-project/vue3-company/backend/static/
   ```

通过以上调整，您的静态文件应该能够正常访问了。如果问题仍然存在，请根据错误日志中的具体信息进一步排查。





## 总结

这个实现提供了完整的后台管理功能，包括：

1. 用户认证系统（基于JWT）
2. 用户管理（增删改查、状态管理）
3. 部门管理（支持层级结构）
4. 角色管理
5. 菜单管理（支持树形结构）
6. 商品管理

所有API都遵循RESTful规范，并且包含了适当的权限控制。管理员可以管理所有资源，普通用户只能查看商品信息，经理用户可以管理商品。

你可以根据需要进一步扩展这个基础框架，添加更多功能或自定义逻辑。





![profile](https://assets.alicdn.com/g/qwenweb/qwen-webui-fe/0.0.205/static/qwen_icon_light_84.png)

**Qwen3-Max-Preview**2025-09-09 4:25 pm

你希望将启动 Nginx 的命令写成 `.bat` 批处理文件，并放在 **Windows 10 开机启动位置**，实现开机自动运行。

⚠️ 但请注意：**Nginx 需要管理员权限才能绑定 80/443 端口**，而 Windows 的“开机启动文件夹”默认**不会以管理员身份运行程序**，直接放 `.bat` 会失败（报错 `10013: 权限被拒绝`）。

## ✅ 正确解决方案（兼顾你的需求）：

我们将分两步：

1. **制作 `.bat` 文件启动 Nginx**
2. **通过“任务计划程序”开机以管理员身份静默运行该 `.bat` 文件**

> ✅ 这是既满足“使用 bat 文件”，又实现“管理员权限 + 开机自启 + 无弹窗”的最佳方案。 

# 🧩 步骤 1：创建启动 Nginx 的 `.bat` 文件

在你的 Nginx 目录（如 `E:\nginx\`）新建一个文件：

### 文件名：`start_nginx.bat`



```
@echo off

cd /d E:\nginx

start nginx.exe

exit
```



> 💡 说明： 
>
> - `@echo off`：不显示命令行
> - `cd /d E:\nginx`：切换到 nginx 目录（`/d` 支持跨盘符）
> - `start nginx.exe`：启动 nginx（非阻塞方式）
> - `exit`：关闭命令窗口（如果通过双击运行）

✅ 双击测试：右键 → “以管理员身份运行” → 应能正常启动 Nginx

# 🧩 步骤 2：通过“任务计划程序”开机自动以管理员身份运行 `.bat`

这是关键！绕过 UAC，静默提权运行。

## 1. 打开“任务计划程序”

按 `Win + R` → 输入：

```
taskschd.msc
```

→ 回车

## 2. 创建任务（⚠️ 不是“创建基本任务”）

点击右侧 “**创建任务**”

### ➤【常规】选项卡

- 名称：`Start Nginx (Admin)`
- 描述：开机自动以管理员权限启动 Nginx
- ✅ 勾选：**使用最高权限运行**
- ✅ 配置为：**Windows 10**

### ➤【触发器】选项卡 → 新建

- 任务开始：✅ `登录时`（推荐）或 `启动时`
- ✅ 延迟任务时间：`30 秒`（等待网络和系统服务就绪）
- ✅ 重复任务间隔：`无`
- ✅ 启用

> 💡 推荐“登录时”而不是“启动时”，因为“启动时”可能太早，Nginx 依赖的网络服务未准备好。 

### ➤【操作】选项卡 → 新建

- 操作：✅ `启动程序`
- 程序或脚本：`E:\nginx\start_nginx.bat`
- ✅ 起始于（可选）：`E:\nginx\`

### ➤【条件】选项卡（可选优化）

- 取消勾选：`只有在计算机使用交流电源时才启动此任务`（笔记本用户注意）
- 取消勾选：`只有在以下网络连接可用时才启动`（避免网络未就绪失败）

### ➤【设置】选项卡（推荐）

- ✅ 如果任务失败，按以下频率重新启动：`1 分钟`（最多重试 3 次）
- ✅ 如果任务没有按计划启动，尽快启动任务

### ➤ 点击【确定】

→ 如果提示输入密码，输入当前管理员账户密码（或直接点“确定”，部分系统不需要）

# ✅ 步骤 3：测试 & 验证

## 1. 手动运行测试

在任务计划程序中，右键任务 → “运行”，观察：

- 是否弹窗？→ 应该完全静默
- 是否启动 Nginx？→ 用 `tasklist | findstr nginx` 检查

## 2. 重启电脑测试

重启后：

- 登录系统，等待 30~60 秒
- 浏览器访问 `https://yourdomain.com`
- 任务管理器 → 查看 `nginx.exe` 是否在运行

# 🚫 为什么不直接放“启动文件夹”？

Windows 启动文件夹路径：

1

shell:startup

（通常是 `C:\Users\你的用户名\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`）

### ❌ 放 `.bat` 在这里的问题：

- 无法自动提权 → 绑定 80/443 失败
- 会弹出黑窗口（除非用 vbs 隐藏，但仍无权限）
- 用户未登录时不运行（服务可以）

# ✅ 额外技巧：完全隐藏黑窗口（可选）

如果你希望 `.bat` 运行时**连一闪而过的黑窗口都没有**，可以创建一个 `.vbs` 包装器：

### 创建 `start_nginx_silent.vbs`

vbs

```
Set ws = CreateObject("WScript.Shell")

ws.Run "E:\nginx\start_nginx.bat", 0, False
```

然后在“任务计划程序”的【操作】中，启动这个 `.vbs` 文件：

- 程序或脚本：`wscript.exe`
- 参数：`E:\nginx\start_nginx_silent.vbs`
- 起始于：`E:\nginx\`

✅ 效果：完全静默，无任何窗口，后台运行

# ✅ 最终结构建议



E:\nginx\

├── nginx.exe

├── start_nginx.bat          ← 启动脚本

├── start_nginx_silent.vbs   ← 可选：完全隐藏窗口

├── conf\nginx.conf

└── logs\

任务计划程序配置调用 `start_nginx_silent.vbs` 或直接调用 `.bat`（窗口一闪可接受）

# 🎯 总结

|                      |                                         |
| -------------------- | --------------------------------------- |
| 制作`.bat`启动 Nginx | ✅`start_nginx.bat`                      |
| 开机自动运行         | ✅ 任务计划程序（触发器：登录时）        |
| 以管理员身份运行     | ✅ 任务计划程序 → “使用最高权限运行”     |
| 无弹窗静默启动       | ✅ 使用`.vbs`包装`.bat`+`ws.Run ..., 0`  |
| 崩溃自动重启         | ✅ 任务计划程序 → 设置中配置“失败后重启” |

✅ 完成！现在你的 Nginx 将在每次开机登录后，自动以管理员权限静默启动，完美托管你的 Vue 项目！

> 💡 如需停止/重启，可创建 `stop_nginx.bat`： 
>
> ```
> @echo off
> 
> cd /d E:\nginx
> 
> nginx -s stop
> ```
>
> 

如有其他自动化需求（如自动构建、日志清理等），欢迎继续提问！





###### WX: shuaibin99，请我喝一杯咖啡(*￣︶￣)

<img src="images/wechat-qrcode.jpg" alt="1766031980889" style="zoom: 100%;" />