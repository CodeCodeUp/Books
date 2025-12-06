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

# 开发模式启动
mvn spring-boot:run

# 清理并打包（跳过测试）
mvn clean package -DskipTests

# 运行所有测试
mvn test

# 运行单个测试类
mvn test -Dtest=UserServiceTest

# 生产模式运行打包后的 JAR
java -jar target/book-recommendation-1.0.0.jar
```

**注意**: 后端默认运行在 `http://localhost:8080/api`

### Frontend (Vue3)
```bash
cd book-recommendation-frontend

# 首次运行需安装依赖
npm install

# 开发模式启动（支持热重载）
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

**注意**: 前端默认运行在 `http://localhost:3000`

### Algorithm Service (Python Flask)
```bash
cd recommendation-algorithm-service

# 首次运行需安装依赖
pip install -r requirements.txt

# 启动算法服务
python app.py

# 运行算法评估（评估推荐质量）
python run_evaluation.py
```

**注意**:
- 算法服务默认运行在 `http://localhost:5000`
- 需要确保 MySQL 数据库可访问
- 首次启动会预加载数据并构建 TF-IDF 特征矩阵（约 1-2 分钟）

### Docker Deployment
```bash
# 一键启动所有服务（后台运行）
docker-compose up -d

# 启动并查看日志
docker-compose up

# 停止所有服务
docker-compose down

# 查看服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f algorithm-service
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启特定服务
docker-compose restart algorithm-service
```

## Configuration

### Database Configuration

**开发环境** (application.yml):
```yaml
spring:
  datasource:
    url: jdbc:mysql://116.205.244.106:33066/book_recommendation
    username: root
    password: 202358
```

**Docker 环境** (docker-compose.yml):
```yaml
environment:
  DB_HOST: 116.205.244.106
  DB_PORT: 3306
  DB_NAME: book_recommendation
```

**注意**: 开发环境数据库端口为 `33066`，Docker 环境为 `3306`

### Environment Variables

后端服务 (application.yml):
```yaml
jwt:
  secret: bookRecommendationSystemSecretKey2025
  expiration: 25920000000  # 300天（毫秒）

recommendation:
  service:
    url: http://localhost:5000  # 算法服务地址
```

算法服务需要的环境变量:
```bash
DB_HOST=116.205.244.106
DB_PORT=33066  # 开发环境
DB_USER=root
DB_PASSWORD=202358
DB_NAME=book_recommendation
```

### CORS Configuration

后端默认允许的跨域来源:
- `http://localhost:3000` (Vue 开发服务器)
- `http://localhost:5173` (Vite 备用端口)

如需修改，编辑 `book-recommendation-backend/src/main/java/com/bookrs/recommendation/config/WebConfig.java`

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

**前端动画库**:
- GSAP - 高性能 JavaScript 动画引擎
- Lottie-web - After Effects 动画渲染
- Animate.css - CSS3 动画库
- AOS (Animate On Scroll) - 滚动触发动画
- Swiper - 触摸滑动轮播组件
- Particles.js - 粒子背景效果
- Typed.js - 打字机效果

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

### 图书详情页动态推荐详解

**适用场景**：用户浏览图书详情页，查看"相似图书推荐"

**策略矩阵**：

| 图书状态 | 推荐算法 | 标识符 | CF比例范围 |
|:---|:---|:---|:---|
| **CF有 + Content有** | **动态混合** | `dynamic_item_cf_content` | **[40%, 85%]** |
| CF有 + Content无 | 纯协同过滤 | `item_cf_only` | 100% |
| CF无 + Content有 | 纯内容特征 | `content_only` | 0% |
| 两者都无 | 同作者降级 | `same_author_fallback` | 0% |

**动态比例计算公式**（针对图书数据质量）：

```python
# 1. 评分数量得分
quantity_score = min(rating_count / 500, 1.0)

# 2. 协同过滤质量得分
cf_count_score = min(cf_similar_count / 20, 1.0)
cf_quality_score = cf_count_score × cf_avg_similarity

# 3. 综合置信度
confidence = quantity_score × cf_quality_score

# 4. 动态比例
cf_ratio = 0.40 + 0.45 × confidence  # 范围 [40%, 85%]
content_ratio = 1.0 - cf_ratio       # 范围 [15%, 60%]
```

**示例对比**：

| 图书类型 | 评分数 | 相似书数 | 平均相似度 | CF比例 | Content比例 |
|:---|:---|:---|:---|:---|:---|
| 超热门书 | 5000 | 50 | 0.85 | **78%** | 22% |
| 热门书 | 800 | 35 | 0.72 | **68%** | 32% |
| 中等热度 | 150 | 12 | 0.65 | **45%** | 55% |
| 冷门书 | 8 | 3 | 0.40 | **40%** | 60% |

**核心改进**：
- 冷门图书（评分少）：降低协同过滤权重，依赖内容特征
- 热门图书（评分多）：提升协同过滤权重，充分利用用户行为数据
- 平滑过渡：避免固定比例（原7:3）带来的"一刀切"问题
- 与个人推荐一致：两个场景都采用动态策略，论文价值高

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

### 快速启动顺序

**推荐的服务启动顺序**:
1. **算法服务** (必须第一个启动)
   ```bash
   cd recommendation-algorithm-service
   python app.py
   ```
   等待看到：`Running on http://127.0.0.1:5000`

2. **后端服务** (依赖算法服务)
   ```bash
   cd book-recommendation-backend
   mvn spring-boot:run
   ```
   等待看到：`Started BookRecommendationApplication`

3. **前端服务** (最后启动)
   ```bash
   cd book-recommendation-frontend
   npm run dev
   ```
   访问：`http://localhost:3000`

### 健康检查

```bash
# 检查算法服务健康状态
curl http://localhost:5000/health

# 检查后端API (需要先登录获取token)
curl http://localhost:8080/api/books?page=1&size=10
```

### 用户场景测试

推荐按以下顺序测试不同推荐策略：

**1. 有评分 + 有兴趣 (三层混合推荐)**
- 注册新用户 → 选择 5-8 个兴趣主题
- 评分至少 10 本图书（3.5-5.0 分）
- 访问推荐页面
- **验证点**：
  - 观察浏览器控制台/后端日志：`[三层混合]` 字样
  - 推荐结果中 `interest_boosted=True` 的图书排名靠前
  - 返回的 `mixing_strategy='triple_hybrid_with_interest_boost'`
  - 推荐的图书 `theme_id` 应与用户兴趣重叠

**2. 有评分 + 无兴趣 (双层混合推荐)**
- 注册新用户 → 跳过兴趣选择
- 评分至少 10 本图书
- 访问推荐页面
- **验证点**：
  - 观察日志：`[双层混合]` 字样
  - 返回的 `mixing_strategy='dual_hybrid_cf_tfidf'`
  - 推荐结果基于评分相似用户和内容特征

**3. 无评分 + 有兴趣 (兴趣主题推荐)**
- 注册新用户 → 选择兴趣主题
- 不进行任何评分
- 访问推荐页面
- **验证点**：
  - 观察日志：`基于兴趣推荐` 字样
  - 推荐图书的 `theme_id` 全部在用户兴趣列表中
  - 返回的 `algorithm='interest_based'`

**4. 冷启动用户 (热门优质图书)**
- 注册新用户 → 跳过兴趣选择
- 不进行任何评分
- 访问推荐页面
- **验证点**：
  - 返回热门优质图书（avg_rating >= 4.0）
  - 返回的 `algorithm='top_quality_books'`

**5. 图书详情页 - 热门书动态推荐**
- 访问一本热门图书详情页（如评分数 > 500）
- 查看"相似图书推荐"
- **验证点**：
  - 观察日志：`[图书详情动态比例]` 字样
  - CF比例应该较高（70%-85%）
  - 返回的 `mixing_strategy='dynamic_item_cf_content'`
  - `confidence_info.rating_count` 应该较大

**6. 图书详情页 - 冷门书动态推荐**
- 访问一本冷门图书详情页（如评分数 < 50）
- 查看"相似图书推荐"
- **验证点**：
  - CF比例应该较低（40%-50%）
  - Content比例应该较高（50%-60%）
  - `confidence_info.confidence_score` 应该较低

### 算法性能评估

运行评估脚本查看推荐质量指标：
```bash
cd recommendation-algorithm-service
python run_evaluation.py
```

**输出指标**:
- Precision@10 (精确率)
- Recall@10 (召回率)
- F1-Score
- Coverage (覆盖率)
- 用户协同 vs TF-IDF vs 混合推荐对比

## Performance Considerations

- 数据加载器使用增量更新机制，避免全量加载
- TF-IDF特征矩阵在服务启动时预计算
- 协同过滤使用稀疏矩阵优化内存
- 推荐结果支持缓存（Redis）
- 兴趣加权仅对最终推荐列表进行，不对全量数据操作

## Troubleshooting

### 常见问题

**1. 后端启动失败: "Access denied for user 'root'@'...'**
- 检查 `book-recommendation-backend/src/main/resources/application.yml` 中的数据库密码
- 确认数据库端口：开发环境使用 `33066`

**2. 算法服务启动失败: "Can't connect to MySQL server"**
- 确保 MySQL 数据库可访问（`telnet 116.205.244.106 33066`）
- 检查防火墙是否阻止连接
- 验证环境变量 `DB_HOST`、`DB_PORT`、`DB_PASSWORD` 配置正确

**3. 前端无法连接后端: "Network Error"**
- 确认后端已启动（访问 `http://localhost:8080/api/docs`）
- 检查前端 API 基础 URL 配置（应为 `http://localhost:8080/api`）
- 验证 CORS 配置是否允许前端域名

**4. 推荐接口返回空结果**
- 查看后端日志，确认算法服务是否可达
- 检查算法服务日志，查看是否有异常
- 验证用户是否有评分记录或兴趣设置

**5. JWT Token 过期**
- 默认有效期为 300 天 (25920000000 毫秒)
- 如需修改，编辑 `application.yml` 中的 `jwt.expiration`

**6. Docker 部署失败**
- 检查端口是否被占用：`netstat -ano | findstr "8080"` (Windows) 或 `lsof -i:8080` (Linux/Mac)
- 查看具体服务日志：`docker-compose logs -f <service-name>`
- 清理并重新构建：`docker-compose down && docker-compose build --no-cache`

### 日志查看

**后端日志**:
```bash
# Maven 启动时会在控制台输出
# 或查看日志文件（如果配置了文件输出）
tail -f logs/application.log
```

**算法服务日志**:
```bash
# Flask 默认输出到控制台
# 日志级别: INFO
# 关键字搜索: "[三层混合]", "[双层混合]", "ERROR"
```

**Docker 日志**:
```bash
docker-compose logs -f --tail=100 algorithm-service
docker-compose logs -f --tail=100 backend
docker-compose logs -f --tail=100 frontend
```

## Key File Paths

快速定位关键配置文件:

```
book-recommendation-backend/
├── src/main/resources/application.yml       # 后端核心配置
├── src/main/java/com/bookrs/recommendation/
│   ├── config/SecurityConfig.java           # JWT & Spring Security
│   ├── config/WebConfig.java                # CORS 配置
│   └── controller/RecommendationController.java  # 推荐API

book-recommendation-frontend/
├── src/api/user.js                          # 用户API调用
├── src/api/recommendation.js                # 推荐API调用
├── src/stores/user.js                       # Pinia 用户状态
├── src/components/InterestSelector.vue      # 兴趣选择核心组件
└── vite.config.js                           # Vite 构建配置

recommendation-algorithm-service/
├── app.py                                   # Flask API 入口
├── config.py                                # 算法服务配置
├── algorithms/hybrid.py                     # 三层混合推荐核心
├── algorithms/collaborative_filtering.py    # 用户协同过滤
├── algorithms/content_based.py              # TF-IDF 内容推荐
└── data/data_loader.py                      # 数据库连接与加载

docker-compose.yml                           # Docker 部署配置
```