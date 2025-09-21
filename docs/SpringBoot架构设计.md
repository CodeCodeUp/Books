# SpringBoot图书推荐系统架构设计

## 架构决策记录 (ADR-001)

* **状态**: 已接受
* **日期**: 2025-09-20

## 背景 (Context)

本科毕业设计项目，需要设计一个简洁但完整的SpringBoot后端架构。重点突出：
- 清晰的分层架构
- 核心业务功能实现
- 代码的可读性和可维护性
- 适合演示和答辩展示

## 决策 (Decision)

采用**经典三层架构** + **简化DDD概念**的组合：

### 1. 整体架构模式

```
┌─────────────────────────────────────────┐
│            表现层 (Controller)           │
│  UserController | BookController        │
│  RatingController | RecommendController │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│            业务层 (Service)             │
│   UserService | BookService            │
│   RatingService | RecommendService     │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│           数据访问层 (Repository)        │
│   UserMapper | BookMapper              │
│   RatingMapper | RecommendMapper       │
└─────────────────────────────────────────┘
```

### 2. 简化包结构设计

```
com.bookrs.recommendation/
├── controller/                  # 控制器层
│   ├── UserController.java     # 用户管理API
│   ├── BookController.java     # 图书管理API
│   ├── RatingController.java   # 评分管理API
│   └── RecommendController.java # 推荐API
├── service/                     # 业务逻辑层
│   ├── UserService.java
│   ├── BookService.java
│   ├── RatingService.java
│   └── RecommendService.java
├── mapper/                      # 数据访问层
│   ├── UserMapper.java
│   ├── BookMapper.java
│   ├── RatingMapper.java
│   └── RecommendMapper.java
├── entity/                      # 实体类
│   ├── User.java
│   ├── Book.java
│   ├── Rating.java
│   └── Recommendation.java
├── dto/                         # 数据传输对象
│   ├── request/                 # 请求DTO
│   └── response/                # 响应DTO
├── config/                      # 配置类
│   ├── DatabaseConfig.java     # 数据库配置
│   ├── SecurityConfig.java     # 安全配置
│   └── WebConfig.java          # Web配置
├── common/                      # 通用组件
│   ├── Result.java             # 统一返回结果
│   ├── PageResult.java         # 分页结果
│   └── GlobalExceptionHandler.java # 全局异常处理
└── BookRecommendationApplication.java # 启动类
```

### 3. 核心技术栈（简化版）

- **框架**: SpringBoot 3.2
- **安全**: Spring Security + JWT（简化版）
- **数据访问**: MyBatis Plus
- **数据库**: MySQL 8.0
- **文档**: SpringDoc OpenAPI（用于API文档）
- **工具**: Lombok（减少样板代码）

### 4. 设计原则

#### 4.1 分层清晰
- Controller层：处理HTTP请求，参数校验
- Service层：核心业务逻辑
- Mapper层：数据库操作

#### 4.2 职责单一
- 每个Service专注一个业务领域
- 每个Controller对应一个资源类型

#### 4.3 简单实用
- 避免过度设计
- 专注功能实现
- 代码易读易懂

## 后果 (Consequences)

### 积极影响
- **简单易懂**: 经典三层架构，容易理解和实现
- **开发效率**: 减少样板代码，快速开发
- **演示友好**: 架构清晰，便于展示和讲解
- **学习成本**: 技术栈适中，适合本科水平

### 消极影响
- **扩展性**: 相比复杂架构扩展性稍弱
- **企业级特性**: 缺少一些企业级监控和治理功能

### 权衡考虑
- 选择此架构是为了：
  - 符合毕业设计的范围和复杂度
  - 突出核心业务功能
  - 便于代码展示和技术答辩
  - 在有限时间内完成高质量实现