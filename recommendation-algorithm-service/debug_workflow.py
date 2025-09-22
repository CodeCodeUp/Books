#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试评分后重新计算流程
"""

import requests
import json

def test_rating_workflow():
    """测试评分后的完整工作流程"""
    print("=== 测试评分后重新计算流程 ===\n")
    
    # 测试用户ID
    test_user_id = 300001  # 假设是新注册用户
    test_book_id = "0002005018"  # 一个存在的图书ID
    
    try:
        # 1. 检查算法服务是否运行
        print("1. 检查算法服务状态...")
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ 算法服务运行正常")
        else:
            print("   ❌ 算法服务异常")
            return
        
        # 2. 模拟用户评分（调用SpringBoot接口）
        print(f"\n2. 模拟用户 {test_user_id} 对图书 {test_book_id} 评分...")
        rating_response = requests.post(
            f"http://localhost:8080/api/ratings/rate",
            params={
                'userId': test_user_id,
                'bookId': test_book_id, 
                'rating': 4.5
            },
            timeout=10
        )
        
        if rating_response.status_code == 200:
            print("   ✅ 评分成功")
            print("   📋 查看后端日志，应该有'已触发用户XXX的推荐预计算'")
        else:
            print(f"   ❌ 评分失败: {rating_response.text}")
            return
        
        # 3. 等待预计算完成
        print("\n3. 等待预计算完成...")
        import time
        time.sleep(5)
        
        # 4. 检查缓存文件是否生成
        print("4. 检查缓存文件...")
        import os
        cache_file = f"models/cache/user_{test_user_id}_recommendations.json"
        
        if os.path.exists(cache_file):
            print("   ✅ 缓存文件已生成")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            print(f"   📊 推荐数量: {len(cache_data.get('recommendations', []))}")
        else:
            print("   ❌ 缓存文件未生成")
        
        # 5. 测试推荐API（应该返回缓存结果）
        print("\n5. 测试推荐API...")
        recommend_response = requests.post(
            "http://localhost:5000/api/recommend/user-based",
            json={
                'user_id': test_user_id,
                'top_n': 5,
                'min_rating': 3.0
            },
            timeout=10
        )
        
        if recommend_response.status_code == 200:
            result = recommend_response.json()
            if result.get('success'):
                recommendations = result['data']['recommendations']
                print(f"   ✅ 成功获取 {len(recommendations)} 个推荐")
                print("   📋 算法服务日志应显示'从缓存返回推荐结果'")
            else:
                print(f"   ❌ 推荐失败: {result.get('message')}")
        else:
            print(f"   ❌ API调用失败: {recommend_response.text}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_rating_workflow()