USE campus_academic;

CREATE TABLE IF NOT EXISTS stu_student (
  student_id VARCHAR(20) PRIMARY KEY COMMENT 'STU+时间戳',
  name VARCHAR(30) NOT NULL,
  sex CHAR(1) DEFAULT '0',
  id_card VARCHAR(18) UNIQUE,
  phone VARCHAR(11),
  dept_id BIGINT,
  class_id BIGINT,
  enroll_year YEAR,
  is_final CHAR(1) DEFAULT '0',
  avatar VARCHAR(255),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS stu_student_file (
  student_id VARCHAR(20) PRIMARY KEY,
  family_info TEXT,
  health_info TEXT,
  award_punish TEXT,
  remark TEXT,
  emergency_contact VARCHAR(30),
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_file_student FOREIGN KEY (student_id) REFERENCES stu_student(student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS stu_class (
  class_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  class_name VARCHAR(50) NOT NULL,
  dept_id BIGINT,
  grade YEAR,
  head_teacher_id BIGINT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS aca_course (
  course_id VARCHAR(20) PRIMARY KEY,
  course_name VARCHAR(100) NOT NULL,
  course_code VARCHAR(20) UNIQUE,
  credit DECIMAL(3,1) DEFAULT 3.0,
  hours INT DEFAULT 48,
  dept_id BIGINT,
  status CHAR(1) DEFAULT '0',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS aca_scheduling (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  course_id VARCHAR(20),
  teacher_id BIGINT,
  classroom_id BIGINT,
  scheduling_day DATE COMMENT '具体日期',
  section_type CHAR(1) COMMENT '1:1-2节 2:3-4节 3:5-6节 4:7-8节',
  scheduling_type CHAR(1) DEFAULT '1' COMMENT '1有课 0停课',
  UNIQUE KEY uk_teacher_day_section (teacher_id, scheduling_day, section_type),
  UNIQUE KEY uk_room_day_section (classroom_id, scheduling_day, section_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS aca_enrollment (
  enroll_id VARCHAR(20) PRIMARY KEY,
  student_id VARCHAR(20) NOT NULL,
  course_id VARCHAR(20) NOT NULL,
  schedule_id BIGINT,
  status CHAR(1) DEFAULT '0' COMMENT '0待缴费 1已选 2已退 5已取消',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_student (student_id),
  INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS aca_exam (
  exam_id VARCHAR(20) PRIMARY KEY,
  course_id VARCHAR(20),
  exam_name VARCHAR(100) NOT NULL,
  exam_time DATETIME,
  paper_id BIGINT,
  status CHAR(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS aca_score (
  score_id VARCHAR(20) PRIMARY KEY,
  student_id VARCHAR(20) NOT NULL,
  course_id VARCHAR(20) NOT NULL,
  exam_id VARCHAR(20),
  score DECIMAL(5,2),
  gpa_point DECIMAL(3,2),
  semester VARCHAR(20),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_stu_course_sem (student_id, course_id, semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 示例数据
INSERT IGNORE INTO stu_class(class_id, class_name, dept_id, grade) VALUES
(1,'计科2101',2,2021),(2,'软工2101',3,2021),(3,'计科2201',2,2022);

INSERT IGNORE INTO stu_student(student_id, name, sex, id_card, phone, dept_id, class_id, enroll_year) VALUES
('20240101','张三','0','110101200001011234','13800001001',2,1,2024),
('20240102','李四','1','110101200002021234','13800001002',2,1,2024),
('20240103','王五','0','110101200003031234','13800001003',3,2,2024);

INSERT IGNORE INTO aca_course(course_id, course_name, course_code, credit, hours, dept_id) VALUES
('COUR20240101','高等数学','MATH101',4.0,64,2),
('COUR20240102','大学英语','ENG101',3.0,48,2),
('COUR20240103','数据结构','CS201',3.5,56,2),
('COUR20240104','操作系统','CS301',3.0,48,2);

INSERT IGNORE INTO aca_exam(exam_id, course_id, exam_name, exam_time) VALUES
('EXAM20240101','COUR20240101','高等数学期末考','2025-01-10 09:00:00'),
('EXAM20240102','COUR20240103','数据结构期末考','2025-01-12 14:00:00');
