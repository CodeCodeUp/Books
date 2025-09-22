# 图书推荐算法服务

## 项目概述
基于协同过滤与内容特征的图书推荐算法微服务，为图书推荐系统提供核心推荐能力。

## 技术栈
- Python 3.8+
- Flask 2.x
- NumPy + Pandas (数据处理)
- Scikit-learn (机器学习)
- MySQL Connector (数据库连接)

## 服务架构
```
recommendation-algorithm-service/
├── app.py                          # Flask主服务入口
├── config.py                       # 配置文件
├── requirements.txt                # Python依赖
├── algorithms/                     # 推荐算法实现
│   ├── __init__.py
│   ├── collaborative_filtering.py  # 协同过滤算法
│   ├── content_based.py           # 基于内容推荐
│   └── hybrid.py                  # 混合推荐策略
├── data/                          # 数据处理模块
│   ├── __init__.py
│   ├── data_loader.py            # 数据加载器
│   └── preprocessor.py           # 数据预处理
├── models/                        # 训练好的模型存储
├── utils/                         # 工具函数
│   ├── __init__.py
│   ├── similarity.py             # 相似度计算
│   └── evaluator.py              # 算法评估
└── tests/                         # 单元测试
    └── test_algorithms.py
```

## API设计
### 用户协同过滤推荐
- **POST** `/api/recommend/user-based`
- **参数**: user_id, top_n, min_rating
- **返回**: 推荐图书列表

### 物品协同过滤推荐  
- **POST** `/api/recommend/item-based`
- **参数**: user_id, top_n
- **返回**: 推荐图书列表

### 混合推荐
- **POST** `/api/recommend/hybrid`
- **参数**: user_id, strategy, top_n
- **返回**: 推荐图书列表

## 启动服务
```bash
pip install -r requirements.txt
python app.py
```
服务地址：http://localhost:5000