# 下载Book-Crossing数据集
import requests
import zipfile
from pathlib import Path
import os

def download_book_crossing():
    """下载Book-Crossing数据集"""
    print("=== 下载Book-Crossing数据集 ===")
    
    # 尝试多个镜像地址
    urls = [
        "http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip",
        "https://cdn.freecodecamp.org/project-data/books/book-crossings.zip",
        "https://files.grouplens.org/datasets/book-crossing/BX-CSV-Dump.zip"
    ]
    
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    zip_file = data_dir / "BX-CSV-Dump.zip"
    
    if zip_file.exists():
        print(f"数据文件已存在: {zip_file}")
        return extract_data(zip_file)
    
    # 尝试下载
    for i, url in enumerate(urls, 1):
        print(f"尝试地址 {i}: {url}")
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(zip_file, 'wb') as f:
                f.write(response.content)
            
            print(f"下载成功: {zip_file}")
            return extract_data(zip_file)
            
        except Exception as e:
            print(f"地址 {i} 失败: {e}")
    
    print("所有下载地址都失败")
    return False

def extract_data(zip_file):
    """解压数据文件"""
    print(f"解压数据文件: {zip_file}")
    
    extract_dir = zip_file.parent / "book_crossing"
    extract_dir.mkdir(exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"解压完成: {extract_dir}")
        
        # 检查解压的文件
        files = list(extract_dir.glob("*.csv"))
        print(f"解压得到 {len(files)} 个CSV文件:")
        for file in files:
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  {file.name} ({size_mb:.1f} MB)")
        
        return extract_dir
        
    except Exception as e:
        print(f"解压失败: {e}")
        return False

if __name__ == "__main__":
    result = download_book_crossing()
    
    if result:
        print("Book-Crossing数据集下载成功!")
    else:
        print("下载失败，请手动下载数据集")