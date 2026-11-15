# 前端完成版更新说明

本次以用户上传的 `course_management_latest.zip` 为基础，保留原 Django 后端和 React 前端工程结构，主要完善前端页面，没有修改后端业务代码或数据库迁移。

## 本次前端完善

- 学生管理：新增学生账号和资料、姓名/学号/用户名/ID 搜索、账号状态筛选、详情查看、资料编辑、软删除（停用账号）、恢复账号。
- 教师管理：管理员新增教师账号和资料；支持搜索、状态筛选、详情查看、资料编辑；教师只能编辑自己的资料。
- 账号状态：展示后端返回的 `account_active`，学生停用后保留资料与选课历史，并可由管理员恢复。
- 课程中心：显示真实课程编号 `code`、选课人数 `enrollment_count`，增加课程详情；继续支持课程搜索、创建、编辑、选课和删除。
- 保留原有登录、注册、工作台、个人资料、选课记录、系统信息、角色路由和 Token 认证。

## 部署更新

只修改了前端，因此不需要重建后端，也不需要执行数据库迁移。在项目根目录运行：

```bash
docker compose build frontend
docker compose up -d --force-recreate frontend
docker compose ps
```

然后浏览器打开 `http://localhost/`。

## 验证说明

已对全部 TypeScript/TSX 文件执行语法转译检查，没有发现语法错误。当前打包环境无法连接 npm registry，依赖未能完整安装，因此无法在此环境完成 `npm run build` 的完整类型检查和 Vite 生产构建。用户本机 Docker 构建时会按 `frontend/package-lock.json` 执行 `npm ci` 和 `npm run build`；如构建报告类型错误，请把完整输出发回以便针对性修复。
