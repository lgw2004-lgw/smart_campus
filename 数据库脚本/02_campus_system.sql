USE campus_system;

-- 用户
CREATE TABLE IF NOT EXISTS sys_user (
  user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  dept_id BIGINT COMMENT '院系ID',
  user_name VARCHAR(30) NOT NULL COMMENT '登录名',
  user_type CHAR(1) DEFAULT '0' COMMENT '0管理员 1教师 2学生',
  phone VARCHAR(11) UNIQUE,
  password VARCHAR(255) DEFAULT '123456',
  status CHAR(1) DEFAULT '0' COMMENT '0正常 1停用',
  del_flag CHAR(1) DEFAULT '0',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_role (
  role_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_name VARCHAR(30) NOT NULL,
  role_code VARCHAR(30) COMMENT 'role:admin/teacher/student',
  status CHAR(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_role_user (
  user_id BIGINT NOT NULL,
  role_id BIGINT NOT NULL,
  PRIMARY KEY(user_id, role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_menu (
  menu_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  parent_id BIGINT DEFAULT 0,
  menu_name VARCHAR(50) NOT NULL,
  path VARCHAR(200),
  icon VARCHAR(50),
  sort INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_role_menu (
  role_id BIGINT NOT NULL,
  menu_id BIGINT NOT NULL,
  PRIMARY KEY(role_id, menu_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_dept (
  dept_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  dept_name VARCHAR(50) NOT NULL,
  parent_id BIGINT DEFAULT 0,
  order_num INT DEFAULT 0,
  status CHAR(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_dict_type (
  dict_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  dict_name VARCHAR(100) NOT NULL,
  dict_type VARCHAR(100) NOT NULL UNIQUE,
  status CHAR(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_dict_data (
  dict_code BIGINT PRIMARY KEY AUTO_INCREMENT,
  dict_type VARCHAR(100) NOT NULL,
  dict_label VARCHAR(100) NOT NULL,
  dict_value VARCHAR(100) NOT NULL,
  dict_sort INT DEFAULT 0,
  status CHAR(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_notice (
  notice_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  notice_title VARCHAR(100) NOT NULL,
  notice_content TEXT,
  notice_type CHAR(1) DEFAULT '1',
  status CHAR(1) DEFAULT '0',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS health_news (
  news_id VARCHAR(50) PRIMARY KEY,
  news_title VARCHAR(255) NOT NULL,
  news_content TEXT,
  news_source VARCHAR(50),
  imag_url VARCHAR(255),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS hos_banner (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  url VARCHAR(500),
  position INT DEFAULT 0,
  enabled TINYINT DEFAULT 1,
  deleted TINYINT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_login_info (
  info_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_name VARCHAR(30),
  login_account VARCHAR(11),
  ip_addr VARCHAR(50),
  login_status CHAR(1) DEFAULT '0',
  login_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_oper_log (
  oper_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(50),
  oper_name VARCHAR(50),
  oper_url VARCHAR(255),
  oper_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sys_white_name (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  path VARCHAR(255) NOT NULL,
  status CHAR(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 初始化数据
INSERT IGNORE INTO sys_user(user_id, user_name, password, user_type, phone, status) VALUES
(1, 'admin', '$2b$12$KIXxQG7KQM0YQ7YQ7YQ7YO9xQG7KQM0YQ7YQ7YQ7YO9xQG7KQM0YQ7YQ7YQ7YO', '0', '13800000001', '0'),
(2, 'teacher01', '123456', '1', '13800000002', '0'),
(3, 't_1001', '123456', '1', '13800000003', '0');

INSERT IGNORE INTO sys_role(role_id, role_name, role_code) VALUES
(1,'超级管理员','role:admin'),(2,'教师','role:teacher'),(3,'学生','role:student');

INSERT IGNORE INTO sys_role_user(user_id, role_id) VALUES (1,1),(2,2),(3,2);

INSERT IGNORE INTO sys_menu(menu_id, parent_id, menu_name, path, icon, sort) VALUES
(1,0,'首页','/home','House',1),
(2,0,'教务管理','/academic','Reading',2),
(3,2,'课程管理','/academic/course','Notebook',1),
(4,2,'排课管理','/academic/scheduling','Calendar',2),
(5,2,'选课管理','/academic/enrollment','List',3),
(6,2,'成绩管理','/academic/score','DataAnalysis',4),
(7,0,'学生管理','/student','User',3),
(8,7,'学生档案','/student/list','UserFilled',1),
(9,7,'班级管理','/student/class','School',2),
(10,0,'资源管理','/resource','Box',4),
(11,10,'宿舍管理','/resource/dorm','OfficeBuilding',1),
(12,10,'图书管理','/resource/book','ReadingLamp',2),
(13,0,'财务管理','/finance','Wallet',5),
(14,13,'缴费管理','/finance/fee','CreditCard',1),
(15,0,'内容管理','/content','Document',6),
(16,15,'公告管理','/content/notice','Bell',1),
(17,15,'轮播管理','/content/banner','Picture',2),
(18,0,'系统管理','/system','Setting',7),
(19,18,'用户管理','/system/user','User',1),
(20,18,'角色管理','/system/role','Avatar',2),
(21,18,'菜单管理','/system/menu','Menu',3),
(22,18,'院系管理','/system/dept','OfficeBuilding',4),
(23,18,'字典管理','/system/dict','Collection',5),
(24,18,'日志管理','/system/log','Notebook',6);

INSERT IGNORE INTO sys_role_menu(role_id, menu_id) SELECT 1, menu_id FROM sys_menu;
INSERT IGNORE INTO sys_role_menu(role_id, menu_id) VALUES (2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,8),(2,10),(2,11),(2,12);
INSERT IGNORE INTO sys_role_menu(role_id, menu_id) VALUES (3,1),(3,2),(3,5),(3,6),(3,10),(3,12),(3,13),(3,14);

INSERT IGNORE INTO sys_dept(dept_id, dept_name, parent_id, order_num) VALUES
(1,'信息工程学院',0,1),(2,'计算机系',1,1),(3,'软件工程系',1,2),(4,'经济管理学院',0,2);

INSERT IGNORE INTO sys_dict_type(dict_id, dict_name, dict_type) VALUES
(1,'性别','sys_user_sex'),(2,'课程状态','course_status'),(3,'缴费状态','fee_status');

INSERT IGNORE INTO sys_dict_data(dict_code, dict_type, dict_label, dict_value, dict_sort) VALUES
(1,'sys_user_sex','男','0',1),(2,'sys_user_sex','女','1',2),
(3,'course_status','正常','0',1),(4,'course_status','停用','1',2),
(5,'fee_status','未付','0',1),(6,'fee_status','已付','3',2);

INSERT IGNORE INTO hos_banner(id, name, url, position, enabled) VALUES
(1,'开学季','https://via.placeholder.com/1200x400?text=Campus+Banner1',1,1),
(2,'图书馆','https://via.placeholder.com/1200x400?text=Library',2,1);

INSERT IGNORE INTO sys_white_name(path, status) VALUES
('/userAuth/login','0'),('/memberAuth/login','0'),('/banner/loadBanner','0'),('/dictData/type/','0');
