# 智慧校园综合管理系统（Vue3版）

> 基址 `http://127.0.0.1:18367` | 响应信封 `{code,message,data}` | 分页 `{pageNo,pageSize,data:{}} → {list,total}` | 认证头 `token`

## 一键启动

### 后端
```bash
cd campus_server
pip install -r requirements.txt
# 建库
mysql -u root -p < ../数据库脚本/01_init_databases.sql
mysql -u root -p < ../数据库脚本/02_campus_system.sql
mysql -u root -p < ../数据库脚本/03_campus_academic.sql
mysql -u root -p < ../数据库脚本/04_campus_resource.sql
mysql -u root -p < ../数据库脚本/05_campus_finance.sql
mysql -u root -p < ../数据库脚本/06_campus_health.sql
# 修改 campus_server/settings.py 中 DATABASES 密码
python manage.py runserver 18367
```

默认账号：`admin/123456`（超管）、`teacher01/123456`、`20240101/123456`（学生）

### 前端
```bash
cd campus-admin
npm install
npm run dev  # 默认 http://127.0.0.1:5173，代理到 18367
```

## 核心闭环
建档(学生) → 排课 → 选课 → 缴费(模拟微信Native) → 考试 → 成绩 → 归档

## 目录
见 `智慧校园-Vue3版-业务流程手册+库表设计.md`
