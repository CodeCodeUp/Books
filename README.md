# 图书推荐系统 - 完整项目指南

## 项目概述
基于协同过滤与内容特征的图书馆资源智能化推荐系统，采用前后端分离 + 微服务算法架构实现。

**核心特色**:
- 🤖 **智能推荐算法**: 用户协同过滤 + 物品协同过滤 + 内容特征 + 混合推荐策略
- 📚 **海量数据支持**: 43万+评分记录，27万+图书，7万+用户
- 🎯 **个性化体验**: 基于用户行为和内容特征的双重推荐
- ⚡ **高性能架构**: 缓存机制 + 异步预计算 + 性能优化

## 项目架构

```
Books/
├── book-recommendation-backend/    # SpringBoot后端 ✅
├── book-recommendation-frontend/   # Vue3前端 ✅
├── recommendation-algorithm-service/ # Python算法服务 ✅
├── data/                          # 原始Book-Crossing数据集
├── processed_data/                # 清洗后的训练数据
├── scripts/                       # 数据处理Python脚本
├── docs/                          # 完整项目文档
├── start-backend.bat/.sh          # 后端启动脚本
├── start-frontend.bat/.sh         # 前端启动脚本
├── start-algorithm.bat/.sh        # 算法服务启动脚本 ✅
└── README.md                      # 项目指南(本文件)
```

## 快速启动

### 🔧 环境要求
- **Java**: JDK 17+
- **Node.js**: 16+
- **MySQL**: 8.0
- **Python**: 3.8+

### 📊 数据库准备

#### 1. 数据导入(如需要)
```bash
cd scripts
python final_import.py    # 导入所有数据到MySQL
```

#### 2. 数据库结构修复(必须执行)
```bash
mysql -h 116.205.244.106 -u root -p book_recommendation < book-recommendation-backend/src/main/resources/db/V1.1_Remove_Foreign_Keys.sql
```

### 🚀 启动服务

#### 1. 推荐算法服务
```bash
# Windows
start-algorithm.bat

# Linux/Mac
./start-algorithm.sh
```
- **服务地址**: http://localhost:5000
- **功能**: 用户协同过滤、物品协同过滤推荐算法

#### 2. 后端服务
```bash
# Windows
start-backend.bat

# Linux/Mac  
./start-backend.sh
```
- **服务地址**: http://localhost:8080
- **API文档**: http://localhost:8080/api/swagger-ui.html

#### 3. 前端服务
```bash
# Windows
start-frontend.bat

# Linux/Mac
./start-frontend.sh
```
- **访问地址**: http://localhost:3000

## 技术栈详情

### 推荐算法服务
- **框架**: Python Flask + Flask-CORS
- **算法**: NumPy + Pandas + Scikit-learn
- **数据库**: SQLAlchemy + PyMySQL
- **缓存**: 本地文件缓存系统
- **性能**: 共同用户预筛选 + 批量相似度计算

### 后端技术栈
- **框架**: SpringBoot 3.1.5
- **安全**: Spring Security + JWT + BCrypt密码加密
- **数据访问**: MyBatis Plus + 分页插件
- **数据库**: MySQL 8.0 + 专业版本管理
- **文档**: SpringDoc OpenAPI 3
- **工具**: Lombok + Maven

### 前端技术栈  
- **框架**: Vue 3 + Composition API
- **UI组件**: Element Plus + 图标库
- **状态管理**: Pinia
- **路由**: Vue Router 4 + 路由守卫
- **HTTP**: Axios + 请求/响应拦截器
- **构建**: Vite

## 核心功能

### ✅ 已实现功能

#### 推荐算法
- **用户协同过滤**: 基于相似用户偏好的个性化推荐，F1-Score 0.39%
- **物品协同过滤**: 基于评分模式相似度的图书推荐  
- **内容特征推荐**: 基于图书内容和用户特征匹配，F1-Score 0.27%
- **混合推荐策略**: 智能组合多算法，协同过滤70% + 内容特征30%
- **性能优化**: 候选预筛选，计算时间从30分钟→几秒钟
- **算法评估**: 留存验证法科学评估，相比基线提升387%

#### 用户管理
- 用户注册(自增ID从300001开始)
- 用户登录(密码加密验证)
- 个人信息管理
- 登录状态保持(JWT + localStorage)

#### 图书管理
- 图书分页浏览(27万+图书)
- 关键词搜索(标题/作者)
- 热门图书展示(基于评分排序)
- 最新图书展示(基于出版年份)
- 图书详情查看
- **相似图书推荐**: 物品协同过滤，"喜欢这本书的用户也喜欢"

#### 评分系统
- 0-5分评分，支持0.5分间隔
- 实时更新图书平均评分
- 评分后自动触发推荐预计算

#### 系统架构
- 前后端分离架构
- 微服务推荐算法
- RESTful API设计
- 统一结果封装
- 跨域配置
- 完整JWT认证

### 🔄 开发中功能
- 混合推荐策略
- 推荐结果评价反馈

### 📋 待开发功能
- 基于内容的推荐算法
- 图书收藏功能
- 推荐解释优化

## 数据库信息

```
连接信息:
Host: 116.205.244.106:3306
Database: book_recommendation
Username: root
Password: 202358hjq

当前数据量:
用户表(users): 77,805条 + 新注册用户
图书表(books): 271,360条
评分表(ratings): 433,671条 + 新评分
收藏表(favorites): 0条
推荐表(recommendations): 0条
```

## 开发进度

### 第一阶段 ✅ (数据处理)
- [x] Book-Crossing数据集下载和处理
- [x] 数据清洗和质量分析  
- [x] MySQL数据库设计和导入

### 第二阶段 ✅ (Web系统)
- [x] SpringBoot后端架构搭建
- [x] Vue前端项目搭建
- [x] 用户管理功能实现
- [x] 图书管理功能实现
- [x] 前后端集成配置

### 第三阶段 📋 (推荐算法)
- [ ] 协同过滤算法实现
- [ ] 内容特征提取算法  
- [ ] 混合推荐策略
- [ ] 算法评估和优化

## 故障排除

### 常见问题
1. **后端启动失败**: 检查Java版本和MySQL连接
2. **前端启动失败**: 执行`npm install`安装依赖
3. **用户注册失败**: 确保执行了V1.1数据库修复脚本
4. **跨域问题**: 检查WebConfig配置

### 技术支持
- **项目文档**: `docs/`目录下的详细文档
- **数据库版本**: `book-recommendation-backend/src/main/resources/db/`
- **API文档**: 启动后端后访问swagger-ui

---

**项目状态**: 基础架构完成，核心功能可用  
**最后更新**: 2025-09-21  
**当前版本**: v1.1