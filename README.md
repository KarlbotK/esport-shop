# 🎮 ShopAgent — 电竞装备电商平台

> 基于 FastAPI + Vue 3 的全栈电竞装备（鼠标 / 键盘 / 耳机 / 鼠标垫 / 电竞椅）电商平台。

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00a393?logo=fastapi)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4-4fc08d?logo=vue.js)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📋 目录

- [功能概览](#-功能概览)
- [技术栈](#-技术栈)

---

## ✨ 功能概览

### 👤 用户端

| 功能 | 说明 |
|------|------|
| 🔐 用户注册 / 登录 | JWT 无状态认证，BCrypt 密码哈希 |
| 🏠 商品浏览 | 全品类商品列表 + 分类/品牌/关键词/价格筛选 + 分页 |
| 📄 商品详情 | SPU/SKU 多层展示，规格选择，缓存加速 |
| 🛒 购物车 | 本地持久化购物车，数量调整，金额计算 |
| 📦 下单 | 库存校验 + 扣减 + 订单确认邮件通知 |
| ⚡ 秒杀 | 高并发秒杀，防超卖防重复，内存锁 |
| 🤖 AI 推荐 | DeepSeek 智能对话，函数调用精准搜索与对比 |

### 🛠️ 销售端 (SALES)

| 功能 | 说明 |
|------|------|
| ➕ 商品管理 | SPU 增删改，SKU 库存管理 |
| 📂 分类管理 | 分类增删 |
| 📊 销售仪表盘 | SPU/SKU 统计、24h 浏览、热度排行 |
| 📋 操作日志 | 行为审计追溯 |

### 📈 管理端 (ADMIN)

| 功能 | 说明 |
|------|------|
| 👥 销售团队管理 | 创建/删除销售人员，重置密码 |
| 📉 销售报表 | 销售排行、趋势图、销售汇总 |
| 🚨 异常检测 | 3-Sigma 实时异常预警 |
| 🔄 定时任务 | 热度排行榜刷新（每小时）、协同过滤计算（每日凌晨） |

---

## 🛠 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| **FastAPI** (异步) | Web 框架 |
| **SQLAlchemy 2.0** (async) | ORM，异步 MySQL 访问 |
| **aiomysql** | MySQL 异步驱动 |
| **Pydantic v2** | 数据校验 + Settings 管理 |
| **PyJWT** | JWT 令牌签发与验证 |
| **passlib[bcrypt]** | 密码哈希 |
| **OpenAI SDK** | DeepSeek API 调用（函数调用） |
| **APScheduler** | 定时任务调度 |
| **cachetools** | 内存 TTLCache（替代 Redis） |
| **aiosmtplib** | 异步邮件发送 |

### 前端

| 技术 | 用途 |
|------|------|
| **Vue 3** (Composition API) | 前端框架 |
| **Vue Router 4** | 路由管理 + 导航守卫 |
| **Pinia** | 状态管理 |
| **Axios** | HTTP 客户端（拦截器 + 统一错误处理） |
| **Vite** | 构建工具 + 开发代理 |

### 数据

| 组件 | 说明 |
|------|------|
| **MySQL 8.0+** | 关系数据库（ums_/pms_/oms_/sms_ 表前缀） |
| **内存 TTLCache** | 4 个命名空间（SPU 详情 / 用户资料 / 热度 / 协同过滤） |
| **item_similarity 表** | 协同过滤 Jaccard 相似度矩阵 |

---

## 👨‍💻 作者

**KarlbotK** — [GitHub](https://github.com/KarlbotK)
