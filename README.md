# 图书推荐系统 - 项目运行指南

## 项目架构

```
Books/
├── book-recommendation-backend/    # SpringBoot后端
├── book-recommendation-frontend/   # Vue前端
├── scripts/                       # 数据处理脚本
├── processed_data/               # 清洗后数据
└── docs/                        # 项目文档
```

## 快速启动

### 1. 数据准备（如需要）
```bash
cd scripts
python final_import.py    # 导入所有数据到MySQL
```

### 2. 启动后端服务
```bash
# Windows
start-backend.bat

# Linux/Mac  
./start-backend.sh
```
访问地址：http://localhost:8080/api/swagger-ui.html

### 3. 启动前端服务
```bash
# Windows
start-frontend.bat

# Linux/Mac
./start-frontend.sh
```
访问地址：http://localhost:3000

## 技术栈

### 后端
- SpringBoot 3.2
- MyBatis Plus
- MySQL 8.0
- SpringDoc OpenAPI

### 前端  
- Vue 3
- Element Plus
- Pinia
- Vue Router
- Axios

## 核心功能

- ✅ 用户注册/登录
- ✅ 图书浏览/搜索
- ✅ 分页展示
- ✅ 图书详情查看
- 🔄 评分功能（开发中）
- 🔄 推荐算法（开发中）

## 数据库信息

```
Host: 116.205.244.106:3306
Database: book_recommendation
用户表: 77,805条
图书表: 271,360条
评分表: 433,671条
```

## 开发状态

当前已完成基础架构搭建，具备：
- 完整的前后端分离架构
- 用户管理功能
- 图书管理功能
- 数据库完整集成

下一步将实现评分功能和推荐算法。