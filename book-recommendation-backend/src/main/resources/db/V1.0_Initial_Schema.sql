- V1.0_Initial_Schema.sql
-- 初始数据库表结构创建

-- 1. 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '登录用户名',
    password VARCHAR(255) NOT NULL COMMENT '加密密码',
    email VARCHAR(100) UNIQUE DEFAULT NULL COMMENT '邮箱',
    nickname VARCHAR(50) DEFAULT NULL COMMENT '昵称',
    location VARCHAR(255) DEFAULT NULL COMMENT '地理位置',
    age INT DEFAULT NULL COMMENT '年龄',
    age_group VARCHAR(20) DEFAULT NULL COMMENT '年龄分组',
    country VARCHAR(100) DEFAULT NULL COMMENT '国家',
    avatar_url VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
    status TINYINT DEFAULT 1 COMMENT '用户状态（1:正常 0:禁用）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login_at TIMESTAMP DEFAULT NULL COMMENT '最后登录时间',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_age_group (age_group),
    INDEX idx_country (country),
    INDEX idx_status (status)
) ENGINE=InnoDB AUTO_INCREMENT=300001 DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 图书表
CREATE TABLE IF NOT EXISTS books (
    book_id VARCHAR(20) PRIMARY KEY COMMENT '图书ID(ISBN)',
    title VARCHAR(500) NOT NULL COMMENT '图书标题',
    author VARCHAR(200) DEFAULT NULL COMMENT '作者',
    publisher VARCHAR(200) DEFAULT NULL COMMENT '出版社',
    year INT DEFAULT NULL COMMENT '出版年份',
    image_url_s VARCHAR(500) DEFAULT NULL COMMENT '小图片URL',
    image_url_m VARCHAR(500) DEFAULT NULL COMMENT '中图片URL',
    image_url_l VARCHAR(500) DEFAULT NULL COMMENT '大图片URL',
    avg_rating DECIMAL(3,2) DEFAULT 0.00 COMMENT '平均评分',
    rating_count INT DEFAULT 0 COMMENT '评分数量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_author (author),
    INDEX idx_year (year),
    INDEX idx_avg_rating (avg_rating),
    INDEX idx_title (title(100)),
    FULLTEXT idx_search (title, author)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书信息表';

-- 3. 评分表
CREATE TABLE IF NOT EXISTS ratings (
    rating_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '评分记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    book_id VARCHAR(20) NOT NULL COMMENT '图书ID',
    rating DECIMAL(2,1) NOT NULL COMMENT '评分(1.0-5.0)',
    rating_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '评分时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_user_book (user_id, book_id),
    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_rating (rating),
    INDEX idx_rating_date (rating_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户评分表';

-- 4. 收藏表
CREATE TABLE IF NOT EXISTS favorites (
    favorite_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '收藏记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    book_id VARCHAR(20) NOT NULL COMMENT '图书ID',
    favorite_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    UNIQUE KEY uk_user_book (user_id, book_id),
    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- 5. 推荐记录表
CREATE TABLE IF NOT EXISTS recommendations (
    recommend_id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '推荐记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    book_id VARCHAR(20) NOT NULL COMMENT '图书ID',
    algorithm_type VARCHAR(50) NOT NULL COMMENT '推荐算法类型',
    score DECIMAL(5,4) NOT NULL COMMENT '推荐分数',
    reason VARCHAR(500) DEFAULT NULL COMMENT '推荐理由',
    is_clicked BOOLEAN DEFAULT FALSE COMMENT '是否被点击',
    recommend_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '推荐时间',
    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_algorithm_type (algorithm_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='推荐记录表';