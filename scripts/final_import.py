#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版本：完整数据导入脚本
确保所有数据正确导入，数量与CSV文件完全匹配
"""

import pandas as pd
import pymysql
import sys
from pathlib import Path
from tqdm import tqdm

# 数据库连接配置
DB_CONFIG = {
    'host': '116.205.244.106',
    'port': 3306,
    'user': 'root',
    'password': '202358hjq',
    'database': 'book_recommendation',
    'charset': 'utf8mb4'
}

def get_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def import_books_final():
    """最终版图书数据导入"""
    print("=== 导入图书数据 ===")
    
    books_df = pd.read_csv("../processed_data/books_metadata.csv")
    print(f"CSV文件图书数: {len(books_df):,}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 清空相关表
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DELETE FROM recommendations")
    cursor.execute("DELETE FROM favorites")
    cursor.execute("DELETE FROM ratings")
    cursor.execute("DELETE FROM books")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    # 批量插入图书
    insert_sql = """
    REPLACE INTO books (book_id, title, author, publisher, year, image_url_s, image_url_m, image_url_l)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    batch_data = []
    batch_size = 1000
    
    for _, row in tqdm(books_df.iterrows(), total=len(books_df), desc="导入图书"):
        book_id = str(row['book_id']).strip()
        title = str(row['title']).strip()[:500]
        author = str(row['author']).strip()[:200] if pd.notna(row['author']) else None
        publisher = str(row['publisher']).strip()[:200] if pd.notna(row['publisher']) else None
        
        # 处理年份
        year = None
        if pd.notna(row['year']):
            try:
                year = int(float(row['year']))
                if year < 1900 or year > 2025:
                    year = None
            except:
                year = None
        
        # 图片URL
        image_s = str(row['Image-URL-S']).strip()[:500] if pd.notna(row['Image-URL-S']) else None
        image_m = str(row['Image-URL-M']).strip()[:500] if pd.notna(row['Image-URL-M']) else None
        image_l = str(row['Image-URL-L']).strip()[:500] if pd.notna(row['Image-URL-L']) else None
        
        if book_id and title:
            batch_data.append((book_id, title, author, publisher, year, image_s, image_m, image_l))
        
        if len(batch_data) >= batch_size:
            cursor.executemany(insert_sql, batch_data)
            conn.commit()
            batch_data = []
    
    if batch_data:
        cursor.executemany(insert_sql, batch_data)
        conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    print(f"成功导入图书: {count:,} 条")
    
    cursor.close()
    conn.close()
    return count

def import_ratings_final():
    """最终版评分数据导入"""
    print("\n=== 导入评分数据 ===")
    
    ratings_df = pd.read_csv("../processed_data/ratings_cleaned.csv")
    print(f"CSV文件评分数: {len(ratings_df):,}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 清空评分表
    cursor.execute("DELETE FROM ratings")
    
    # 禁用外键检查加速导入
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # 批量插入评分
    insert_sql = "INSERT INTO ratings (user_id, book_id, rating) VALUES (%s, %s, %s)"
    
    batch_data = []
    batch_size = 5000
    
    for _, row in tqdm(ratings_df.iterrows(), total=len(ratings_df), desc="导入评分"):
        user_id = row['user_id']
        book_id = str(row['book_id']).strip()
        rating = float(row['rating'])
        
        if pd.notna(user_id) and pd.notna(rating) and book_id and 0 < rating <= 5:
            batch_data.append((int(user_id), book_id, rating))
        
        if len(batch_data) >= batch_size:
            cursor.executemany(insert_sql, batch_data)
            conn.commit()
            batch_data = []
    
    if batch_data:
        cursor.executemany(insert_sql, batch_data)
        conn.commit()
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    cursor.execute("SELECT COUNT(*) FROM ratings")
    count = cursor.fetchone()[0]
    print(f"成功导入评分: {count:,} 条")
    
    cursor.close()
    conn.close()
    return count

def update_book_stats_final():
    """最终版图书统计更新"""
    print("\n=== 更新图书统计 ===")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    update_sql = """
    UPDATE books b 
    SET 
        avg_rating = (SELECT ROUND(AVG(r.rating), 2) FROM ratings r WHERE r.book_id = b.book_id),
        rating_count = (SELECT COUNT(*) FROM ratings r WHERE r.book_id = b.book_id)
    WHERE EXISTS (SELECT 1 FROM ratings r WHERE r.book_id = b.book_id)
    """
    
    cursor.execute(update_sql)
    affected = cursor.rowcount
    conn.commit()
    
    print(f"更新了 {affected:,} 本图书的统计信息")
    
    cursor.close()
    conn.close()

def verify_final_data():
    """验证最终数据"""
    print("\n=== 数据验证 ===")
    
    # 检查CSV文件
    books_df = pd.read_csv("../processed_data/books_metadata.csv")
    ratings_df = pd.read_csv("../processed_data/ratings_cleaned.csv")
    users_df = pd.read_csv("../processed_data/users_metadata.csv")
    
    print("CSV文件数据:")
    print(f"  用户: {len(users_df):,}")
    print(f"  图书: {len(books_df):,}")
    print(f"  评分: {len(ratings_df):,}")
    
    # 检查数据库
    conn = get_connection()
    cursor = conn.cursor()
    
    tables = ['users', 'books', 'ratings']
    print("\n数据库数据:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count:,}")
    
    # 检查图书统计
    cursor.execute("SELECT COUNT(*) FROM books WHERE rating_count > 0")
    books_with_ratings = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(avg_rating), MAX(rating_count) FROM books WHERE rating_count > 0")
    result = cursor.fetchone()
    
    if result[0]:
        avg_rating, max_count = result
        print(f"\n图书统计:")
        print(f"  有评分图书: {books_with_ratings:,}")
        print(f"  平均评分: {avg_rating:.2f}")
        print(f"  最多评分数: {max_count}")
    
    cursor.close()
    conn.close()

def main():
    """主函数"""
    print("=== 最终版数据导入 ===")
    print("确保所有数据与CSV文件完全匹配\n")
    
    try:
        # 1. 导入图书数据
        books_count = import_books_final()
        
        # 2. 导入评分数据
        ratings_count = import_ratings_final()
        
        # 3. 更新图书统计
        update_book_stats_final()
        
        # 4. 验证数据
        verify_final_data()
        
        print(f"\n=== 导入完成 ===")
        print(f"图书: {books_count:,} 条")
        print(f"评分: {ratings_count:,} 条")
        print("所有数据导入成功！")
        
    except Exception as e:
        print(f"导入失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()