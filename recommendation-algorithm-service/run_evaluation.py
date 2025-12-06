#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行推荐算法评估实验
用于毕业论文的实验数据生成
"""

import sys
import os

# 获取脚本所在目录（recommendation-algorithm-service）
script_dir = os.path.dirname(os.path.abspath(__file__))
# 将项目根目录添加到Python路径
sys.path.insert(0, script_dir)

from utils.evaluator import RecommendationEvaluator
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """运行算法评估实验"""
    print("="*60)
    print("[算法评估] 图书推荐算法评估实验")
    print("="*60)
    print("[实验设置]:")
    print("   - 评估方法: 留存验证法")
    print("   - 数据分割: 80%训练 + 20%测试")
    print("   - 评估指标: Precision@10, Recall@10, F1-Score")
    print("   - 喜好定义: 评分>=4.0分")
    print("   - 评估用户: 活跃用户(>=10条评分)")
    print("="*60)

    try:
        # 初始化评估器
        print("\n[初始化] 正在初始化评估器...")
        evaluator = RecommendationEvaluator()

        # 运行综合评估
        print("\n[评估中] 开始算法评估实验...")
        results = evaluator.run_comprehensive_evaluation()

        # 生成评估报告
        print("\n[生成报告] 正在生成评估报告...")
        report = evaluator.generate_evaluation_report(results)

        print("\n[完成] 评估实验完成!")
        print("[结果] 结果文件保存在 evaluation_results/ 目录")
        print("[用途] 可用于毕业论文的实验数据已生成")

    except Exception as e:
        print(f"\n[错误] 评估实验失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()