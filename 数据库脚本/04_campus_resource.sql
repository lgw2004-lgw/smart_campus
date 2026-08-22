USE campus_resource;

CREATE TABLE IF NOT EXISTS res_building (
  building_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  building_name VARCHAR(50) NOT NULL,
  dept_id BIGINT,
  floors INT DEFAULT 6,
  status CHAR(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS res_room (
  room_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  building_id BIGINT NOT NULL,
  room_no VARCHAR(20) NOT NULL,
  capacity INT DEFAULT 4,
  occupied INT DEFAULT 0,
  status CHAR(1) DEFAULT '0',
  UNIQUE KEY uk_building_room (building_id, room_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS res_dorm_assign (
  assign_id VARCHAR(20) PRIMARY KEY,
  student_id VARCHAR(20) NOT NULL UNIQUE,
  building_id BIGINT NOT NULL,
  room_id BIGINT NOT NULL,
  bed_no TINYINT DEFAULT 1,
  status CHAR(1) DEFAULT '0',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS res_book (
  book_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  book_name VARCHAR(200) NOT NULL,
  isbn VARCHAR(20) UNIQUE,
  author VARCHAR(100),
  category VARCHAR(50),
  stock INT DEFAULT 10,
  total INT DEFAULT 10,
  del_flag CHAR(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS res_borrow (
  borrow_id VARCHAR(20) PRIMARY KEY,
  student_id VARCHAR(20) NOT NULL,
  book_id BIGINT NOT NULL,
  borrow_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  return_time DATETIME,
  due_time DATETIME,
  status CHAR(1) DEFAULT '0' COMMENT '0借出 1已还 2逾期',
  fine DECIMAL(6,2) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO res_building(building_id, building_name, floors) VALUES
(1,'学1栋',6),(2,'学2栋',6),(3,'学3栋',6);

INSERT IGNORE INTO res_room(room_id, building_id, room_no, capacity, occupied) VALUES
(1,1,'101',4,1),(2,1,'102',4,0),(3,2,'201',4,0),(4,2,'202',4,0),(5,3,'301',6,0);

INSERT IGNORE INTO res_book(book_id, book_name, isbn, author, category, stock, total) VALUES
(1,'深入理解计算机系统','9787111544937','Randal E.Bryant','计算机',5,5),
(2,'算法导论','9787111407010','Thomas H.Cormen','计算机',3,3),
(3,'高等数学(第七版)','9787040396638','同济大学','数学',10,10),
(4,'活着','9787506365437','余华','文学',8,8);
