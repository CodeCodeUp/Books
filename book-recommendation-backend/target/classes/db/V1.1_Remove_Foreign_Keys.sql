-- V1.1_Remove_Foreign_Keys.sql
-- 删除所有外键约束并修改用户表为自增主键

-- 删除外键约束
ALTER TABLE favorites DROP FOREIGN KEY favorites_ibfk_1;
ALTER TABLE favorites DROP FOREIGN KEY favorites_ibfk_2;
ALTER TABLE ratings DROP FOREIGN KEY ratings_ibfk_1;
ALTER TABLE ratings DROP FOREIGN KEY ratings_ibfk_2;
ALTER TABLE recommendations DROP FOREIGN KEY recommendations_ibfk_1;
ALTER TABLE recommendations DROP FOREIGN KEY recommendations_ibfk_2;

-- 修改用户表为自增主键
ALTER TABLE users MODIFY COLUMN user_id INT AUTO_INCREMENT;
ALTER TABLE users AUTO_INCREMENT = 300001;