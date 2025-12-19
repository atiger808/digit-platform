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



## PostgreSQL授权用户

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









###### WX: shuaibin99，请我喝一杯咖啡(*￣︶￣)

<img src="images/wechat-qrcode.jpg" alt="1766031980889" style="zoom: 100%;" />