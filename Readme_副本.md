# Python Web Admin

一个基于 FastAPI 的 Telegram 机器人管理系统。

## 功能特性

### 认证管理
- [x] 管理员登录
- [x] JWT Token 认证
- [x] 权限控制

### 用户管理
- [x] 用户列表查看
- [x] 用户搜索
- [x] 用户统计
- [x] 用户增长图表
- [x] 用户标签管理
- [x] 用户备注功能
- [x] Telegram 用户同步
- [x] 消息发送功能

### 服务器管理
- [x] 添加服务器信息
- [x] 服务器信息汇总
- [x] 服务器到期管理
- [x] 服务器续期功能
- [x] 自动到期提醒
- [x] 定时状态更新

### 机器人配置
- [x] 机器人配置管理
- [x] 多机器人支持
- [x] 机器人状态监控
- [x] 配置测试功能

## 后端技术栈

- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- MySQL
- APScheduler
- JWT

## 前端技术栈

### 核心框架
- Vue 3
- TypeScript
- Vite

### UI 组件
- Element Plus
- Vue Use

### 状态管理
- Pinia

### 路由管理
- Vue Router

### 工具库
- Axios (HTTP 请求)
- Day.js (日期处理)
- ECharts (图表展示)

### 开发工具
- ESLint
- Prettier
- TypeScript
- Vite

### 项目规范
- Vue 3 组合式 API
- TypeScript 类型检查
- ESLint 代码规范
- Git 提交规范

## 数据库设计

### 用户表 (users)
- 基本用户信息
- Telegram 用户信息
- 用户状态管理

### 标签表 (tags)
- 标签管理
- 用户-标签关联

### 服务器表 (server_info)
- 服务器基本信息
- 到期时间管理
- 状态追踪

### 续期记录表 (server_renewals)
- 续期历史记录
- 时间变更追踪

### 机器人配置表 (bot_config)
- 机器人配置信息
- 状态监控
- 多机器人支持

## API 接口

### 认证接口
- POST `/api/v1/auth/login` - 管理员登录

### 用户管理
- GET `/api/v1/users/` - 获取用户列表
- GET `/api/v1/users/sync` - 同步 Telegram 用户
- GET `/api/v1/users/stats` - 获取用户统计
- GET `/api/v1/users/search` - 搜索用户
- GET `/api/v1/users/stats/chart` - 获取用户增长图表
- PUT `/api/v1/users/{user_id}/note` - 更新用户备注
- POST `/api/v1/users/{user_id}/tags` - 添加用户标签
- POST `/api/v1/users/{user_id}/message` - 发送消息给用户

### 服务器管理
- POST `/api/v1/servers/{user_id}` - 添加服务器信息
- POST `/api/v1/servers/{user_id}/{server_id}/renew` - 续期服务器
- DELETE `/api/v1/servers/{user_id}/{server_id}` - 删除服务器
- GET `/api/v1/servers/summary` - 获取服务器信息汇总

### 机器人配置
- GET `/api/v1/bot/config` - 获取机器人配置列表
- POST `/api/v1/bot/config` - 添加机器人配置
- POST `/api/v1/bot/config/{config_id}/test` - 测试机器人配置

## 定时任务
- 每小时更新服务器状态
- 每天早上9点发送到期提醒

## 环境要求
- Python 3.9+
- MySQL 5.7+
- 支持异步的运行环境



