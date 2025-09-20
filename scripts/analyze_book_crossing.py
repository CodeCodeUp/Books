# 分析Book-Crossing数据集结构和数据质量
import pandas as pd
from pathlib import Path

def analyze_book_crossing_data():
    """分析Book-Crossing数据集的结构和质量"""
    print("=== Book-Crossing数据集分析 ===")
    
    data_dir = Path("../data/book_crossing")
    
    if not data_dir.exists():
        print("ERROR: 数据目录不存在，请先下载数据")
        return
    
    # 1. 分析评分数据
    print("\n1. === 评分数据分析 ===")
    try:
        ratings = pd.read_csv(data_dir / "BX-Book-Ratings.csv", 
                             delimiter=';', encoding='latin-1', low_memory=False)
        print(f"评分数据维度: {ratings.shape}")
        print(f"列名: {list(ratings.columns)}")
        print("\n前5行数据:")
        print(ratings.head())
        
        print(f"\n评分分布:")
        print(ratings.iloc[:, 2].value_counts().sort_index())
        
        print(f"\n基本统计:")
        print(f"  总评分数: {len(ratings):,}")
        print(f"  独立用户数: {ratings.iloc[:, 0].nunique():,}")
        print(f"  独立图书数: {ratings.iloc[:, 1].nunique():,}")
        
        # 显式评分vs隐式评分
        explicit_ratings = ratings[ratings.iloc[:, 2] > 0]
        implicit_ratings = ratings[ratings.iloc[:, 2] == 0]
        print(f"  显式评分(1-10): {len(explicit_ratings):,}")
        print(f"  隐式评分(0): {len(implicit_ratings):,}")
        
    except Exception as e:
        print(f"读取评分数据失败: {e}")
    
    # 2. 分析图书数据
    print("\n2. === 图书数据分析 ===")
    try:
        books = pd.read_csv(data_dir / "BX-Books.csv", 
                           delimiter=';', encoding='latin-1', low_memory=False)
        print(f"图书数据维度: {books.shape}")
        print(f"列名: {list(books.columns)}")
        print("\n前3行数据:")
        for i in range(min(3, len(books))):
            book = books.iloc[i]
            print(f"\n第{i+1}本书:")
            for j, col in enumerate(books.columns):
                print(f"  {col}: {book.iloc[j]}")
        
        print(f"\n数据质量分析:")
        print(f"  总图书数: {len(books):,}")
        for col in books.columns:
            missing = books[col].isna().sum()
            missing_pct = (missing / len(books)) * 100
            print(f"  {col} 缺失: {missing:,} ({missing_pct:.1f}%)")
        
        # 出版年份分析
        if 'Year-Of-Publication' in books.columns:
            years = pd.to_numeric(books['Year-Of-Publication'], errors='coerce')
            valid_years = years[(years >= 1900) & (years <= 2023)]
            print(f"\n出版年份分析:")
            print(f"  有效年份数量: {len(valid_years):,}")
            print(f"  年份范围: {valid_years.min():.0f} - {valid_years.max():.0f}")
            print(f"  异常年份数量: {len(years) - len(valid_years):,}")
        
    except Exception as e:
        print(f"读取图书数据失败: {e}")
    
    # 3. 分析用户数据
    print("\n3. === 用户数据分析 ===")
    try:
        users = pd.read_csv(data_dir / "BX-Users.csv", 
                           delimiter=';', encoding='latin-1', low_memory=False)
        print(f"用户数据维度: {users.shape}")
        print(f"列名: {list(users.columns)}")
        print("\n前5行数据:")
        print(users.head())
        
        print(f"\n数据质量分析:")
        print(f"  总用户数: {len(users):,}")
        for col in users.columns:
            missing = users[col].isna().sum()
            missing_pct = (missing / len(users)) * 100
            print(f"  {col} 缺失: {missing:,} ({missing_pct:.1f}%)")
        
        # 年龄分析
        if 'Age' in users.columns:
            ages = pd.to_numeric(users['Age'], errors='coerce')
            valid_ages = ages[(ages >= 10) & (ages <= 100)]
            print(f"\n年龄分析:")
            print(f"  有效年龄数量: {len(valid_ages):,}")
            print(f"  年龄范围: {valid_ages.min():.0f} - {valid_ages.max():.0f}")
            print(f"  平均年龄: {valid_ages.mean():.1f}")
        
    except Exception as e:
        print(f"读取用户数据失败: {e}")

def propose_data_cleaning_strategy():
    """提出数据清洗策略"""
    print("\n\n=== 数据清洗策略建议 ===")
    
    print("\n1. 评分数据清洗:")
    print("   - 保留显式评分(1-10)，去除隐式评分(0)")
    print("   - 将评分范围标准化到1-5分 (rating = original_rating / 2)")
    print("   - 过滤活跃用户: 至少评分5本书")
    print("   - 过滤热门图书: 至少被3个用户评分")
    print("   - 去除重复评分记录")
    
    print("\n2. 图书数据清洗:")
    print("   - 标准化ISBN格式")
    print("   - 处理缺失的书名、作者信息")
    print("   - 清理异常出版年份(设为默认值2000)")
    print("   - 统一出版社名称格式")
    
    print("\n3. 用户数据清洗:")
    print("   - 年龄异常值处理(10-100岁范围外设为NULL)")
    print("   - 地理位置信息标准化")
    print("   - 匿名用户信息处理")

def estimate_final_dataset_size():
    """估算清洗后的数据集大小"""
    print("\n=== 预期清洗后数据集大小 ===")
    
    try:
        data_dir = Path("../data/book_crossing")
        ratings = pd.read_csv(data_dir / "BX-Book-Ratings.csv", 
                             delimiter=';', encoding='latin-1', low_memory=False)
        
        # 显式评分
        explicit_ratings = ratings[ratings.iloc[:, 2] > 0]
        print(f"显式评分: {len(explicit_ratings):,} 条")
        
        # 估算过滤后大小
        # 假设30%的用户是活跃用户，50%的图书是热门图书
        estimated_final_ratings = len(explicit_ratings) * 0.3 * 0.5
        print(f"预估清洗后评分数: {estimated_final_ratings:,.0f} 条")
        
        # 用户和图书数量
        estimated_users = explicit_ratings.iloc[:, 0].nunique() * 0.3
        estimated_books = explicit_ratings.iloc[:, 1].nunique() * 0.5
        print(f"预估用户数: {estimated_users:,.0f}")
        print(f"预估图书数: {estimated_books:,.0f}")
        
        # 数据稀疏度
        sparsity = (1 - estimated_final_ratings / (estimated_users * estimated_books)) * 100
        print(f"预估数据稀疏度: {sparsity:.1f}%")
        
    except Exception as e:
        print(f"无法估算数据集大小: {e}")

if __name__ == "__main__":
    analyze_book_crossing_data()
    propose_data_cleaning_strategy()
    estimate_final_dataset_size()