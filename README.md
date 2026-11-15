# 课程管理系统（Course Management System）

## 1. 项目介绍

这是一个基于 Django REST Framework 开发的课程管理系统后端项目。

系统提供用户认证、角色权限管理、学生管理、教师管理、课程管理以及学生选课等功能。

项目主要面向管理员、教师和学生三种角色，通过 RESTful API 提供服务。

## 2. 技术栈

- Python
- Django
- Django REST Framework
- SQLite
- Django Filter
- DRF Token Authentication
- drf-spectacular
- uv
- MyPy

## 3. 项目结构

```text
course_management/
├── config/
├── users/
├── students/
├── teachers/
├── courses/
├── enrollments/
├── manage.py
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

## 4. 环境要求

- Python 3.14 或项目配置要求的兼容版本
- uv
- Git

## 5. 安装项目

克隆项目：

```bash
git clone <项目仓库地址>
cd course_management
```

安装依赖：

```bash
uv sync
```

复制环境变量示例文件：

```bash
cp .env.example .env
```

根据本地环境修改 `.env`。

## 6. 数据库迁移

生成迁移文件：

```bash
uv run python manage.py makemigrations
```

执行数据库迁移：

```bash
uv run python manage.py migrate
```

## 7. 创建管理员

```bash
uv run python manage.py createsuperuser
```

按照提示设置管理员账号和密码。

## 8. 启动项目

```bash
uv run python manage.py runserver
```

默认开发地址：

```text
http://127.0.0.1:8000/
```

## 9. API 文档

项目使用 drf-spectacular 生成 OpenAPI 文档。

Swagger UI：

```text
http://127.0.0.1:8000/api/docs/
```

ReDoc：

```text
http://127.0.0.1:8000/api/redoc/
```

OpenAPI Schema：

```text
http://127.0.0.1:8000/api/schema/
```

## 10. 用户角色

### 管理员

- 管理学生信息
- 管理教师信息
- 管理课程
- 查看和管理所有选课记录

### 教师

- 查看自己的课程
- 管理授权范围内的课程信息
- 查看自己课程的选课记录

### 学生

- 查看课程
- 选择课程
- 查看自己的选课记录
- 退选课程

具体权限以项目中的 Permission 和 ViewSet 实现为准。

## 11. 主要功能

- 用户注册与 Token 认证
- 学生信息管理
- 教师信息管理
- 课程 CRUD
- 选课与退课
- 重复选课校验
- 课程容量校验
- 数据访问隔离
- 角色权限控制
- 过滤、搜索和排序
- 分页
- API 限流
- 统一异常响应
- Swagger API 文档

## 12. 运行自动化测试

运行全部测试：

```bash
uv run python manage.py test
```

## 13. 代码类型检查

```bash
uv run mypy .
```

## 14. 项目检查

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

## 15. 注意事项

本项目当前使用 SQLite 作为开发数据库。

如果用于生产环境，需要根据实际部署情况配置数据库、密钥、DEBUG、ALLOWED_HOSTS、静态文件和 HTTPS 等。


## 后端管理接口补充

- 管理员可通过 `POST /api/students/` 创建学生账号和学生资料，字段包括 `username`、`password`、`name`、`student_no`、`age`，可选 `email`。
- 管理员可通过 `POST /api/teachers/` 创建教师账号和教师资料，字段包括 `username`、`password`、`name`、`department`，可选 `email`。
- 学生列表支持 `?search=关键词` 搜索姓名、学号、用户名或 ID，也支持 `?id=学生资料ID` 精确筛选；列表项返回 `username` 和 `account_active`。
- 管理员可通过 `GET /api/students/{id}/` 查看学生详情。
- `DELETE /api/students/{id}/` 采用软删除：停用账号、删除旧 Token，但保留学生资料和选课记录。
- 管理员可通过 `POST /api/students/{id}/restore/` 恢复学生账号；恢复后学生需重新登录获取新 Token。
- 课程返回系统生成的唯一 `code`（例如 `CRS00001`）和 `enrollment_count`，并支持按课程编号搜索或精确筛选。

升级已有数据库时执行：

```bash
docker compose exec backend python manage.py migrate
```

该迁移只为课程增加编号字段，并为已有课程补齐编号，不会删除现有业务数据。
