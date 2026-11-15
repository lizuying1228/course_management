# 后端更新说明

## 学生管理
- 学生列表增加用户名、账号启用状态字段。
- 支持按姓名、学号、用户名、学生资料 ID、用户 ID 搜索；支持 `id`、`student_no`、账号状态精确筛选。
- 管理员可以通过 `GET /api/students/{id}/` 查看详情。
- 管理员可以通过 `POST /api/students/` 同时创建 User 账号和 Student 资料；保留使用 `user_id` 绑定已有账号的兼容方式。
- 删除学生改为软删除：停用 User、删除 Token，保留 Student 和 Enrollment。
- 新增 `POST /api/students/{id}/restore/` 恢复账号。
- 新增学生权限和软删除/恢复相关测试。

## 教师管理
- 教师列表增加用户名和账号启用状态。
- 支持按教师姓名、部门、用户名、教师 ID 搜索和筛选。
- 管理员可以通过 `POST /api/teachers/` 同时创建 User 账号和 Teacher 资料；保留 `user_id` 绑定方式。
- 新增教师账号创建测试。

## 课程管理
- Course 新增唯一 `code`，自动生成 `CRS00001` 格式编号。
- 新增 `enrollment_count` 选课人数统计字段。
- 支持按课程编号搜索和精确筛选。
- 新增迁移 `courses.0002_course_code`，会为已有课程补齐编号。
- 新增课程编号和选课人数统计测试。

## 部署更新
更新代码后执行：

```bash
docker compose build backend
docker compose up -d backend
docker compose exec backend python manage.py migrate
```

不要使用 `docker compose down -v`，也不要删除 `mysql_data`。
