#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
协同过滤算法测试脚本
验证内存优化版本是否正常工作
"""

import sys
sys.path.append('.')

from algorithms.collaborative_filtering import UserBasedCollaborativeFiltering
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)

def test_algorithm():
    """测试协同过滤算法"""
    print("=== 协同过滤算法测试 ===\n")
    
    try:
        # 1. 初始化算法
        print("1. 初始化算法...")
        cf = UserBasedCollaborativeFiltering()
        
        # 2. 加载数据
        print("2. 加载数据...")
        cf.load_data()
        print(f"   评分数据: {len(cf.ratings_df):,} 条")
        print(f"   图书数据: {len(cf.books_df):,} 条")
        
        # 3. 测试现有用户的推荐
        test_user_id = 8  # 使用一个已知存在的用户ID
        print(f"\n3. 测试用户 {test_user_id} 的推荐...")
        
        recommendations = cf.get_recommendations(test_user_id, top_n=5)
        
        if recommendations:
            print(f"   成功生成 {len(recommendations)} 个推荐:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec['title'][:50]}... - 预测评分: {rec['predicted_rating']}")
        else:
            print("   没有生成推荐")
        
        # 4. 测试相似用户查找
        print(f"\n4. 测试相似用户查找...")
        similar_users = cf.find_similar_users_efficient(test_user_id, top_k=5)
        
        if similar_users:
            print(f"   找到 {len(similar_users)} 个相似用户:")
            for user in similar_users:
                print(f"   用户 {user['user_id']}: 相似度 {user['similarity']:.3f}")
        else:
            print("   没有找到相似用户")
        
        print(f"\n✅ 算法测试完成，没有内存溢出错误！")
        return True
        
    except Exception as e:
        print(f"\n❌ 算法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_algorithm()
    if success:
        print("\n🎉 算法修复成功，可以重启服务！")
    else:
        print("\n💥 算法仍有问题，需要进一步修复！")