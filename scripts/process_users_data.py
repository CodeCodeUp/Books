# 处理用户数据
import pandas as pd
import numpy as np
from pathlib import Path
import re

def load_and_clean_users_data():
    """加载和清洗用户数据"""
    print("=== 处理用户数据 ===")
    
    try:
        data_dir = Path("../data/book_crossing")
        users = pd.read_csv(data_dir / "BX-Users.csv", 
                           delimiter=';', encoding='latin-1')
        
        print(f"原始用户数据: {len(users):,} 个用户")
        print(f"列名: {list(users.columns)}")
        
        # 重命名列
        users.columns = ['user_id', 'location', 'age']
        
        # 1. 清洗年龄数据
        users['age'] = pd.to_numeric(users['age'], errors='coerce')
        
        # 过滤合理年龄范围
        users.loc[(users['age'] < 10) | (users['age'] > 100), 'age'] = np.nan
        
        print(f"年龄统计:")
        print(f"  有效年龄数量: {users['age'].notna().sum():,}")
        print(f"  年龄范围: {users['age'].min():.0f} - {users['age'].max():.0f}")
        print(f"  平均年龄: {users['age'].mean():.1f}")
        
        # 2. 处理地理位置信息
        users['location'] = users['location'].fillna('Unknown')
        
        # 提取国家信息(地址最后一部分)
        def extract_country(location):
            if pd.isna(location) or location == 'Unknown':
                return 'Unknown'
            parts = str(location).split(',')
            return parts[-1].strip().lower() if parts else 'Unknown'
        
        users['country'] = users['location'].apply(extract_country)
        
        # 3. 年龄分组
        def age_group(age):
            if pd.isna(age):
                return 'Unknown'
            elif age < 18:
                return 'Under 18'
            elif age < 25:
                return '18-24'
            elif age < 35:
                return '25-34'
            elif age < 45:
                return '35-44'
            elif age < 55:
                return '45-54'
            else:
                return '55+'
        
        users['age_group'] = users['age'].apply(age_group)
        
        # 4. 统计信息
        print(f"\n用户数据清洗结果:")
        print(f"  总用户数: {len(users):,}")
        print(f"  有年龄信息: {users['age'].notna().sum():,} ({users['age'].notna().mean()*100:.1f}%)")
        print(f"  年龄分组分布:")
        print(users['age_group'].value_counts())
        
        print(f"\n前10个国家/地区:")
        top_countries = users['country'].value_counts().head(10)
        print(top_countries)
        
        return users
        
    except Exception as e:
        print(f"处理用户数据失败: {e}")
        return None

def filter_active_users(users, ratings):
    """只保留有评分记录的用户"""
    print("\n=== 过滤活跃用户 ===")
    
    if users is None or ratings is None:
        return None
    
    # 获取有评分记录的用户ID
    active_user_ids = set(ratings['user_id'].unique())
    print(f"有评分记录的用户: {len(active_user_ids):,}")
    
    # 过滤用户数据
    active_users = users[users['user_id'].isin(active_user_ids)].copy()
    print(f"匹配的用户数据: {len(active_users):,}")
    
    # 统计活跃用户的人口统计信息
    print(f"\n活跃用户统计:")
    print(f"  有年龄信息: {active_users['age'].notna().sum():,} ({active_users['age'].notna().mean()*100:.1f}%)")
    print(f"  平均年龄: {active_users['age'].mean():.1f}")
    print(f"  年龄分组分布:")
    print(active_users['age_group'].value_counts())
    
    return active_users

def save_users_data(users):
    """保存用户数据"""
    print(f"\n=== 保存用户数据 ===")
    
    if users is None:
        return
    
    data_dir = Path("../processed_data")
    data_dir.mkdir(exist_ok=True)
    users_file = data_dir / "users_metadata.csv"
    
    users.to_csv(users_file, index=False, encoding='utf-8')
    print(f"用户数据保存至: {users_file}")
    print(f"保存的字段: {list(users.columns)}")

def main():
    """主流程"""
    print("=== 补充用户数据处理 ===")
    
    # 1. 加载和清洗用户数据
    users = load_and_clean_users_data()
    
    # 2. 加载评分数据
    try:
        ratings = pd.read_csv("../processed_data/ratings_cleaned.csv")
        print(f"\n加载评分数据: {len(ratings):,} 条")
    except Exception as e:
        print(f"加载评分数据失败: {e}")
        ratings = None
    
    # 3. 过滤活跃用户
    active_users = filter_active_users(users, ratings)
    
    # 4. 保存数据
    save_users_data(active_users)
    
    print(f"\n=== 用户数据处理完成 ===")

if __name__ == "__main__":
    main()