#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试特定用户相似度计算
"""

import sys
sys.path.append('.')

from data.data_loader import DataLoader
import pandas as pd

def debug_user_similarity():
    """调试用户278855和用户183的相似度"""
    print("=== 调试用户相似度计算 ===\n")
    
    loader = DataLoader()
    
    try:
        # 加载评分数据
        print("1. 加载评分数据...")
        ratings_df = loader.load_ratings_data()
        
        # 检查两个用户的评分
        user1_id = 278855
        user2_id = 183
        
        print(f"\n2. 检查用户 {user1_id} 的评分:")
        user1_ratings = ratings_df[ratings_df['user_id'] == user1_id]
        print(f"   用户 {user1_id} 评分了 {len(user1_ratings)} 本图书")
        if not user1_ratings.empty:
            print(f"   评分图书: {list(user1_ratings['book_id'].values)}")
        
        print(f"\n3. 检查用户 {user2_id} 的评分:")
        user2_ratings = ratings_df[ratings_df['user_id'] == user2_id]
        print(f"   用户 {user2_id} 评分了 {len(user2_ratings)} 本图书")
        if not user2_ratings.empty:
            print(f"   评分图书: {list(user2_ratings['book_id'].values)}")
        
        print(f"\n4. 检查共同评分图书:")
        if not user1_ratings.empty and not user2_ratings.empty:
            user1_books = set(user1_ratings['book_id'].values)
            user2_books = set(user2_ratings['book_id'].values)
            common_books = user1_books & user2_books
            
            print(f"   共同评分图书数: {len(common_books)}")
            if common_books:
                print(f"   共同图书: {list(common_books)}")
                
                # 显示共同图书的评分
                for book_id in common_books:
                    user1_rating = user1_ratings[user1_ratings['book_id'] == book_id]['rating'].iloc[0]
                    user2_rating = user2_ratings[user2_ratings['book_id'] == book_id]['rating'].iloc[0]
                    print(f"     图书 {book_id}: 用户{user1_id}评{user1_rating}分, 用户{user2_id}评{user2_rating}分")
        
        # 5. 检查特定图书的评分情况
        target_book = "Folio Junior: L'histoire De Monsieur Sommer"
        print(f"\n5. 检查图书 '{target_book}' 的评分情况:")
        
        # 先查找这本书的book_id
        books_df = loader.load_book_data()
        target_book_info = books_df[books_df['title'].str.contains(target_book, na=False)]
        
        if not target_book_info.empty:
            book_id = target_book_info.iloc[0]['book_id']
            print(f"   图书ID: {book_id}")
            
            book_ratings = ratings_df[ratings_df['book_id'] == book_id]
            print(f"   总评分数: {len(book_ratings)}")
            
            # 检查指定用户是否评分了这本书
            user1_book_rating = book_ratings[book_ratings['user_id'] == user1_id]
            user2_book_rating = book_ratings[book_ratings['user_id'] == user2_id]
            
            if not user1_book_rating.empty:
                print(f"   用户 {user1_id} 评分: {user1_book_rating['rating'].iloc[0]}")
            else:
                print(f"   用户 {user1_id} 未评分")
                
            if not user2_book_rating.empty:
                print(f"   用户 {user2_id} 评分: {user2_book_rating['rating'].iloc[0]}")
            else:
                print(f"   用户 {user2_id} 未评分")
        else:
            print(f"   未找到图书 '{target_book}'")
        
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_user_similarity()