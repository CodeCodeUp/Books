#!/bin/bash
# 推荐算法服务启动脚本

echo "=== 启动图书推荐算法服务 ==="

cd recommendation-algorithm-service

echo "检查Python环境..."
python --version

echo "安装依赖..."
pip install -r requirements.txt

echo "启动算法服务..."
echo "算法服务地址: http://localhost:5000"
echo "API接口:"
echo "  POST /api/recommend/user-based  - 用户协同过滤推荐"
echo "  POST /api/recommend/similar-users - 获取相似用户"
echo "  GET  /api/algorithm/info - 算法信息"
echo "  GET  /health - 健康检查"

python app.py