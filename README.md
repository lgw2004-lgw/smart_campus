# 智慧校园综合管理系统（Vue3版）

> 基址 `http://127.0.0.1:18367` | 响应信封 `{code,message,data}` | 分页 `{pageNo,pageSize,data:{}} → {list,total}` | 认证头 `token`

## 技术栈

- 后端：Django 5.2 + PyMySQL + PyJWT + bcrypt + qrcode，多库路由（system/academic/resource/finance 分库）
- 管理端（教师/教务/管理员）：Vue3 + Vite + TS + Pinia + Element Plus，端口 `5173`
- 学生端（C端）：Vue3 + Vite + TS，端口 `5174`

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
# 修改 campus_server/settings.py 中 DATABASES 密码
python manage.py runserver 18367 --noreload
```

默认账号：`admin/123456`（超级管理员）、各学院教务处账号（角色6，如计算机学院 `0001/123456`）、教师（角色7，工号如 `000100016`）、学生端用学号登录。

### 前端
```bash
cd campus-admin && npm install && npm run dev   # http://127.0.0.1:5173
cd campus-student && npm install && npm run dev # http://127.0.0.1:5174
```

## 核心闭环

建档(学生) → 培养方案 → 排课发布 → 选课 → 缴费(模拟微信Native) → 上课考勤 → 考试 → 成绩逐级上报 → 归档

## 功能模块

### 教务管理（campus-admin）
- **课程管理**：课程类型字典（公共基础/通识/学科基础/专业核心/专业方向），按学院隔离
- **培养方案**：按专业维护四年课程计划；学生端可查个人培养方案
- **排课管理**：按专业从培养方案批量排课、手动排课、发布/撤回（未发布不可选课）
- **考试管理**：考试名称/课程/类型（期中·期末·补考·重修）/日期时间/教室；**管理员可发布全校考试，学院教务仅能为本院课程排考并发布**
- **成绩管理 · 逐级上报**：
  1. 教师填写成绩（草稿）→ 提交后教师锁定不可改
  2. 学院教务确认 → 上报管理员，教务锁定不可改（可退回教师）
  3. 管理员终审 → 仅管理员可修改（可重开）
  - 状态：`0教师草稿 → 1待教务确认 → 2待管理员终审 → 3已终审`
- **选课管理**：选课需已发布排课+已缴当前学期总学费；重修自动计费

### 学生服务（campus-student）
- 首页真实数据：待缴费门数/可选课程数/在借图书/GPA/宿舍分配/公告数/今日课表（按星期与节次实时渲染）
- 选课大厅 / 我的选课 / 我的课表（学期+教学周筛选）/ 个人培养方案 / 考试信息（仅显示已发布且本人已选课程的考试）
- 一卡通缴费（学费总单+零散缴费，扫码模拟支付）/ 宿舍服务（按书院筛选、管理员定时发布开放选题）/ 图书馆（书库检索+分类筛选、我的借阅归还）

### 数据隔离
- 教务处账号按学院隔离：课程/排课/考试/成绩/班级/学生列表均只可见本院数据
- 教师按所属学院查看本院课程数据

## 学号规则

`入学年份(4)+学院(2位)+专业(4位)+专业内序号(4位)`，例 `20260110010001`
