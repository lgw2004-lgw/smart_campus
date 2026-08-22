USE campus_finance;

CREATE TABLE IF NOT EXISTS fee_order (
  order_id VARCHAR(20) PRIMARY KEY COMMENT 'ORD+时间戳',
  student_id VARCHAR(20) NOT NULL,
  order_amount DECIMAL(10,2) DEFAULT 0,
  order_status CHAR(1) DEFAULT '0' COMMENT '0未付 3已付',
  ch_id VARCHAR(20) COMMENT '关联选课批次(enrollIds逗号拼接)',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  pay_time DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fee_order_item (
  item_id VARCHAR(20) PRIMARY KEY,
  order_id VARCHAR(20) NOT NULL,
  ref_id VARCHAR(20) COMMENT 'enroll_id/book_id',
  item_name VARCHAR(100),
  item_price DECIMAL(8,2) DEFAULT 0,
  item_num INT DEFAULT 1,
  item_amount DECIMAL(10,2) DEFAULT 0,
  INDEX idx_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fee_refund (
  refund_id VARCHAR(20) PRIMARY KEY COMMENT 'RFD',
  order_id VARCHAR(20) NOT NULL,
  refund_amount DECIMAL(10,2) DEFAULT 0,
  refund_status CHAR(1) DEFAULT '0' COMMENT '0申请 1完成',
  reason VARCHAR(255),
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
