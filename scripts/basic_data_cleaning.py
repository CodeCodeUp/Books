# Book-Crossing数据清洗和处理（第一阶段：基础清洗）
import pandas as pd
import numpy as np
from pathlib import Path
import re

def load_ratings_data():
    """加载和清洗评分数据（基础清洗）"""
    print("=== 加载评分数据 ===")
    
    try:
        data_dir = Path("../data/book_crossing")
        ratings = pd.read_csv(data_dir / "BX-Book-Ratings.csv", 
                             delimiter=';', encoding='latin-1')
        
        print(f"原始评分数据: {len(ratings):,} 条")
        
        # 重命名列
        ratings.columns = ['user_id', 'book_id', 'rating']
        
        # 基础清洗：只保留显式评分(1-10)
        explicit_ratings = ratings[ratings['rating'] > 0].copy()
        print(f"显式评分: {len(explicit_ratings):,} 条")
        
        # 评分标准化到1-5分
        explicit_ratings['rating'] = explicit_ratings['rating'] / 2.0
        explicit_ratings['rating'] = explicit_ratings['rating'].clip(1, 5)
        
        return explicit_ratings
        
    except Exception as e:
        print(f"加载评分数据失败: {e}")
        return None

def load_books_data():
    """加载图书数据"""
    print("\n=== 加载图书数据 ===")
    
    try:
        data_dir = Path("../data/book_crossing")
        books_file = data_dir / "BX-Books.csv"
        
        # 跳过格式错误的行
        books = pd.read_csv(books_file, delimiter=';', encoding='latin-1', 
                           on_bad_lines='skip')
        
        print(f"成功加载: {len(books):,} 本图书")
        
        # 重命名列
        column_mapping = {
            'ISBN': 'book_id',
            'Book-Title': 'title', 
            'Book-Author': 'author',
            'Year-Of-Publication': 'year',
            'Publisher': 'publisher'
        }
        
        existing_mapping = {k: v for k, v in column_mapping.items() if k in books.columns}
        books = books.rename(columns=existing_mapping)
        
        # 基础清洗
        if 'year' in books.columns:
            books['year'] = pd.to_numeric(books['year'], errors='coerce')
            books['year'] = books['year'].fillna(2000)
            books['year'] = books['year'].clip(1900, 2023)
        
        # 处理缺失值
        string_columns = ['title', 'author', 'publisher']
        for col in string_columns:
            if col in books.columns:
                books[col] = books[col].fillna('Unknown')
        
        print(f"清洗后图书数据: {len(books):,} 本")
        return books
        
    except Exception as e:
        print(f"加载图书数据失败: {e}")
        return None

def save_basic_cleaned_data(ratings, books):
    """保存基础清洗后的数据"""
    print("\n=== 保存基础清洗数据 ===")
    
    data_dir = Path("../processed_data")
    data_dir.mkdir(exist_ok=True)
    
    if ratings is not None:
        # 基础评分数据
        ratings_file = data_dir / "ratings_cleaned.csv"
        ratings.to_csv(ratings_file, index=False, encoding='utf-8')
        print(f"清洗后评分数据: {ratings_file} ({len(ratings):,} 条)")
    
    if books is not None:
        # 图书元数据
        books_file = data_dir / "books_metadata.csv"
        books.to_csv(books_file, index=False, encoding='utf-8')
        print(f"图书元数据: {books_file} ({len(books):,} 本)")

def show_data_summary(ratings, books):
    """显示数据摘要"""
    print("\n=== 第一阶段数据清洗总结 ===")
    
    if ratings is not None:
        print(f"评分数据:")
        print(f"  总评分数: {len(ratings):,}")
        print(f"  用户数: {ratings['user_id'].nunique():,}")
        print(f"  图书数: {ratings['book_id'].nunique():,}")
        print(f"  评分分布: {ratings['rating'].value_counts().sort_index().to_dict()}")
    
    if books is not None:
        print(f"\n图书数据:")
        print(f"  总图书数: {len(books):,}")
        if 'year' in books.columns:
            print(f"  出版年份范围: {books['year'].min():.0f} - {books['year'].max():.0f}")

def main():
    """主流程 - 第一阶段基础数据清洗"""
    print("=== Book-Crossing数据清洗（第一阶段）===")
    
    # 1. 加载和基础清洗评分数据
    ratings = load_ratings_data()
    
    # 2. 加载和基础清洗图书数据
    books = load_books_data()
    
    # 3. 保存基础清洗后的数据
    save_basic_cleaned_data(ratings, books)
    
    # 4. 显示数据摘要
    show_data_summary(ratings, books)
    
    print("\n=== 第一阶段：基础数据清洗完成 ===")
    print("数据已准备好进行下一步的探索和分析")

if __name__ == "__main__":
    main()