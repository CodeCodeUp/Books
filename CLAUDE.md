# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

图书推荐系统 - 基于**三层混合推荐算法**的图书馆资源智能化推荐系统。采用三层微服务架构：Vue3前端 + SpringBoot后端 + Python算法服务。

**核心创新点**：
- 动态置信度混合推荐（协同过滤比例 50%-90% 自适应）
- 显式兴趣加权（用户主动选择的兴趣优先级提升）
- 三层架构（隐式行为 + 内容特征 + 显式偏好）

## Development Commands

### Backend (SpringBoot)
```bash
cd book-recommendation-backend
mvn spring-boot:run                    # 启动后端服务 (端口8080)
mvn clean package -DskipTests          # 打包
mvn test                               # 运行测试
```

### Frontend (Vue3)
```bash
cd book-recommendation-frontend
npm install                            # 安装依赖
npm run dev                            # 启动开发服务器 (端口3000)
npm run build                          # 生产构建
```

### Algorithm Service (Python Flask)
```bash
cd recommendation-algorithm-service
pip install -r requirements.txt        # 安装依赖
python app.py                          # 启动算法服务 (端口5000)
python run_evaluation.py               # 运行算法评估
```

### Docker Deployment
```bash
docker-compose up -d                   # 一键启动所有服务
docker-compose down                    # 停止所有服务
docker-compose logs -f                 # 查看日志
```

### Quick Start Scripts
```bash
# Windows
start-backend.bat                      # 启动后端
start-frontend.bat                     # 启动前端
start-algorithm.bat                    # 启动算法服务

# Linux/Mac
./start-backend.sh
./start-frontend.sh
./start-algorithm.sh
```

## Architecture

### Three-Tier Microservices
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────────────┐
│  Vue3 Frontend      │───►│  SpringBoot Backend │───►│  Python Algorithm Service   │
│  (Port 3000)        │    │  (Port 8080)        │    │  (Port 5000)                │
│                     │    │                     │    │                             │
│  Element Plus       │    │  JWT + Security     │    │  ┌──────────────────────┐  │
│  Pinia / Router     │    │  MyBatis Plus       │    │  │ User-CF (协同过滤)   │  │
│  Axios              │    │  RESTful API        │    │  │ Item-CF (物品协同)   │  │
│  InterestSelector   │    │  User Interests     │    │  │ Content (TF-IDF)     │  │
└─────────────────────┘    └─────────────────────┘    │  │ Hybrid (三层混合)    │  │
                                     │                 │  └──────────────────────┘  │
                                     ▼                 └─────────────────────────────┘
                           ┌─────────────────────┐
                           │  MySQL 8.0          │
                           │  (116.205.244.106)  │
                           │  • users            │
                           │  • books (theme_id) │
                           │  • ratings          │
                           │  • book_theme       │
                           │  • user_interests   │
                           └─────────────────────┘
```

### Backend Structure (com.bookrs.recommendation)
- `controller/` - REST API endpoints
  - `UserController` - 用户管理、兴趣保存
  - `BookController` - 图书查询、详情
  - `RatingController` - 评分提交
  - `RecommendationController` - 推荐接口
  - `CategoryController` - 主题分类（31个兴趣主题）
- `service/` - Business logic layer
  - `UserInterestService` - 用户兴趣管理（增删查改）
- `mapper/` - MyBatis Plus data access
- `entity/` - JPA entities
  - `User` - 用户信息（简化注册：username + password + age）
  - `Book` - 图书信息（包含 `theme_id` 字段用于兴趣匹配）
  - `Rating` - 用户评分
  - `BookTheme` - 图书主题（31个预定义兴趣类别）
  - `UserInterest` - 用户兴趣关联表（多对多）
- `config/` - Security, JWT, CORS, MyBatis configurations
- `common/` - Result wrapper, PageResult

### Frontend Structure (src/)
- `views/` - Page components
  - `CompleteProfile.vue` - 用户注册后完善信息（Step1: 年龄，Step2: 兴趣选择）
  - `Recommendations.vue` - 个性化推荐页面
  - `MyRatings.vue` - 我的评分历史
- `components/` - Reusable components
  - `InterestSelector.vue` - **核心组件**：Apple风格3D浮动气泡兴趣选择器
    - 智能网格布局（2×2/3×2/3×3 自适应）
    - 8项/页分页显示
    - 随机选择、全选/清空功能
- `api/` - Axios API modules
  - `user.js` - 用户兴趣保存 API
  - `recommendation.js` - 推荐请求 API
- `stores/` - Pinia state management (user.js)
- `router/` - Vue Router with guards

### Algorithm Service Structure (recommendation-algorithm-service/)
- `algorithms/` - **核心推荐算法**
  - `collaborative_filtering.py` - 用户协同过滤
    - 余弦相似度计算
    - 最少共同评分：2本图书
    - 相似度阈值：> 0.6
    - 最多50个相似用户
  - `item_based_cf.py` - 物品协同过滤
    - 基于评分矩阵的图书相似度
    - 用于图书详情页"相似图书推荐"
  - `content_based.py` - **内容特征推荐**（已重构）
    - TF-IDF文本特征（1500维：标题+作者+出版社）
    - 用户特征判断：`age` OR `interests`（已移除 `country`）
    - `_recommend_by_interests()` - **新增**：基于兴趣主题推荐
    - `_recommend_by_age()` - **新增**：基于年龄偏好推荐
    - 年龄偏好规则：青少年偏好新书，老年偏好经典
  - `hybrid.py` - **三层混合推荐**（核心创新）
    - `_get_triple_hybrid_recommendations()` - **新增**：CF + TF-IDF + 兴趣加权
    - `_get_dual_hybrid_recommendations()` - **新增**：CF + TF-IDF（无兴趣）
    - `_apply_interest_boost()` - **新增**：兴趣加权（匹配 theme_id 提升30%）
    - 动态比例计算：cf_ratio = 0.5 + 0.4 × confidence
- `data/data_loader.py` - 数据库连接与数据加载
  - `get_user_interests()` - **新增**：获取用户兴趣主题ID列表
  - `get_books_by_themes()` - **新增**：根据主题ID获取相关图书
  - 增量更新机制（避免全量加载）
- `utils/` - Cache, evaluator, similarity calculations
- `app.py` - Flask API endpoints

## Key API Endpoints

### Backend API (prefix: /api)
- `POST /users/register` - 注册（返回 JWT token 自动登录）
- `POST /users/login` - 登录
- `GET/PUT /users/{userId}` - 用户信息
- `GET /users/{userId}/interests` - **获取用户兴趣列表**
- `POST /users/{userId}/interests` - **保存用户兴趣**（覆盖式更新）
- `GET /themes` - 获取所有图书主题（31个兴趣类别）
- `GET /books` - 分页查询图书
- `GET /books/{bookId}` - 图书详情
- `POST /ratings` - 提交评分
- `GET /recommendations/user/{userId}` - **个性化推荐**（调用算法服务）

### Algorithm API (port 5000)
- `POST /api/recommend/user-based` - **混合推荐**（主要接口）
  - 根据用户状态自动选择策略（三层/双层/兴趣/热门）
- `POST /api/recommend/item-based` - 物品协同过滤
- `POST /api/recommend/similar-items` - 相似图书推荐（图书详情页）
- `POST /api/recommend/content-based` - 纯内容特征推荐
- `POST /api/recommend/similar-users` - 查找相似用户（调试用）
- `POST /api/cache/clear` - 清除用户推荐缓存
- `POST /api/cache/precompute` - 预计算推荐结果

## Recommendation Strategy Matrix (推荐策略矩阵)

| 用户状态 | 推荐算法 | 标识符 | 说明 |
|:---|:---|:---|:---|
| **有评分 + 有兴趣** | **三层混合** | `triple_hybrid_with_interest_boost` | **核心创新点** |
| 有评分 + 有年龄 | 双层混合 | `dual_hybrid_cf_tfidf` | CF + TF-IDF |
| 有评分 + 无特征 | 双层混合 | `dual_hybrid_cf_tfidf` | 纯数据驱动 |
| 无评分 + 有兴趣 | 兴趣主题推荐 | `interest_based` | 直接匹配 theme_id |
| 无评分 + 有年龄 | 年龄偏好推荐 | `age_based` | 年代匹配 |
| 无评分 + 无特征 | 热门优质图书 | `top_quality_books` | 冷启动降级 |

### 三层混合推荐详解

**适用场景**：用户有评分历史 AND 用户选择了兴趣

**核心流程**：
```
1. 获取协同过滤推荐（CF）- 基于相似用户
2. 获取TF-IDF内容推荐（Content）- 基于评分历史的用户画像
3. 动态计算混合比例：
   - 置信度 = (相似用户数/50) × 平均相似度
   - cf_ratio = 0.5 + 0.4 × 置信度  # 范围 [50%, 90%]
   - content_ratio = 1 - cf_ratio   # 范围 [10%, 50%]
4. 兴趣加权：
   - 查询每个推荐图书的 theme_id
   - IF theme_id IN 用户兴趣列表:
       - similarity *= 1.3  (TF-IDF相似度提升30%)
       - content_score *= 1.3  (内容特征分提升30%)
       - predicted_rating *= 1.15  (协同过滤预测评分提升15%)
       - 标记 interest_boosted = True
5. 按动态比例混合 CF 和 Content
6. 返回 Top-N 推荐
```

**论文亮点**：
- 动态置信度混合：避免固定比例的弊端
- 显式兴趣加权：用户主动选择的偏好权重更高
- 多源融合：隐式行为（评分）+ 内容特征（TF-IDF）+ 显式偏好（兴趣）

## Database Schema

核心表：`users`, `books`, `ratings`, `book_theme`, `user_interests`

### users 表
- 简化注册：`username` + `password` + `age`（无 email/location）
- `age` 用于年龄偏好推荐
- 已移除 `country` 字段

### books 表
- **重要字段**：`theme_id` - 用于兴趣主题匹配
- 其他字段：`title`, `author`, `publisher`, `year`, `avg_rating`, `rating_count`

### book_theme 表
- 31个预定义兴趣主题
- 字段：`theme_id`, `theme_name_en`, `theme_name_zh`, `description`

### user_interests 表（多对多关联）
- 用户与兴趣主题的关联
- 字段：`user_id`, `theme_id`
- 唯一约束：`UNIQUE(user_id, theme_id)`

### ratings 表
- 用户评分记录
- 用于协同过滤和TF-IDF用户画像构建

## UI Design

Apple-style minimalist design with light blue theme (#5ac8fa).

**核心组件**：`InterestSelector.vue`
- 3D浮动气泡选择器
- 智能网格布局（2×2/3×2/3×3 自适应）
- 8项/页分页显示
- 32个兴趣主题，每个主题对应 Emoji 图标
- 随机选择、全选/清空功能

## User Flow

1. **注册** → 自动登录（JWT token 返回）
2. **完善信息** → CompleteProfile
   - Step 1: 输入年龄
   - Step 2: 选择兴趣（InterestSelector）- **关键步骤**
3. **浏览图书** → 评分
4. **获取推荐** → 根据用户状态自动选择推荐策略
   - 有兴趣 + 有评分：三层混合推荐（最佳效果）
   - 仅有兴趣：兴趣主题推荐
   - 仅有评分：双层混合推荐
   - 无任何数据：热门优质图书

## Algorithm Implementation Details

### 协同过滤（Collaborative Filtering）
- 相似度计算：余弦相似度
- 最少共同评分：2本图书
- 相似度阈值：> 0.6
- 预测评分：加权平均

### TF-IDF内容特征（Content-Based）
- 文本特征：`title + author + publisher`
- TF-IDF维度：1500维
- 数值特征：`year`（标准化）+ `avg_rating`（标准化）
- 总维度：~1502维（稀疏矩阵）

### 动态混合比例算法
```python
置信度 = (相似用户数 / 50) × 平均相似度
协同过滤比例 = 0.5 + 0.4 × 置信度  # [0.5, 0.9]
内容特征比例 = 1.0 - 协同过滤比例  # [0.1, 0.5]
```

### 兴趣加权策略
| 评分类型 | 提升幅度 | 上限 |
|:---|:---|:---|
| `similarity` (TF-IDF) | × 1.3 | ≤ 1.0 |
| `content_score` | × 1.3 | ≤ 1.0 |
| `predicted_rating` (CF) | × 1.15 | ≤ 5.0 |

## Data Flow (兴趣推荐数据流)

```
用户注册 → 填写年龄 → 选择兴趣(theme_ids) → 保存到 user_interests 表
                                                           ↓
推荐请求 → 获取用户信息 → get_user_interests(user_id) → [theme_ids]
                                                           ↓
                              get_books_by_themes(theme_ids) → 匹配 books.theme_id
                                                           ↓
                              兴趣加权 → _apply_interest_boost() → 提升匹配图书评分
                                                           ↓
                              动态混合 → CF + Content → 返回 Top-N 推荐
```

## Testing Recommendations

推荐测试以下用户场景：

1. **有评分 + 有兴趣**
   - 观察日志：`[三层混合]` 字样
   - 验证推荐结果中 `interest_boosted=True` 的图书排名靠前
   - 验证 `mixing_strategy='triple_hybrid_with_interest_boost'`

2. **有评分 + 无兴趣**
   - 观察日志：`[双层混合]` 字样
   - 验证 `mixing_strategy='dual_hybrid_cf_tfidf'`

3. **无评分 + 有兴趣**
   - 观察日志：`基于兴趣推荐` 字样
   - 验证推荐结果中图书的 `theme_id` 在用户兴趣列表中
   - 验证 `algorithm='interest_based'`

4. **冷启动用户（无评分 + 无兴趣）**
   - 验证返回热门优质图书
   - 验证 `algorithm='top_quality_books'`

## Performance Considerations

- 数据加载器使用增量更新机制，避免全量加载
- TF-IDF特征矩阵在服务启动时预计算
- 协同过滤使用稀疏矩阵优化内存
- 推荐结果支持缓存（Redis）
- 兴趣加权仅对最终推荐列表进行，不对全量数据操作