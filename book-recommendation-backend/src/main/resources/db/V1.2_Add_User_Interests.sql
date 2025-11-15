-- V1.2_Add_User_Interests.sql
-- 创建用户兴趣表

-- 创建用户兴趣表（多对多关系）
CREATE TABLE IF NOT EXISTS user_interests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    user_id INT NOT NULL COMMENT '用户ID',
    theme_id INT NOT NULL COMMENT '兴趣主题ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_user_theme (user_id, theme_id),
    INDEX idx_user_id (user_id),
    INDEX idx_theme_id (theme_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户兴趣表';
