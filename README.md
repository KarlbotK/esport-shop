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
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [API 文档](#-api-文档)
- [部署](#-部署)
- [截图](#-截图)

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

## 🚀 快速开始

### 前置条件

- Python 3.12+
- Node.js 20+
- MySQL 8.0+
- DeepSeek API 密钥（[申请地址](https://platform.deepseek.com)）

### 1. 克隆仓库

```bash
git clone https://github.com/KarlbotK/esport-shop.git
cd esport-shop
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入真实的数据库密码、DeepSeek API Key、SMTP 授权码等
```

### 3. 初始化数据库

```bash
mysql -u root -p < init.sql
# 可选：生成更多测试数据
python seed_data.py
```

### 4. 启动后端

```bash
# 创建并激活虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8080
```

后端启动于 `http://localhost:8080`，自动 API 文档：`http://localhost:8080/docs`

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端启动于 `http://localhost:3000`，开发服务器自动代理 `/api` 到 `:8080`

### 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `admin123` |
| 普通用户 | 自行注册 | — |

---

## 📁 项目结构

```
esport-shop/
├── .env.example          # 环境变量模板（提交用）
├── .gitignore
├── requirements.txt      # Python 依赖
├── init.sql              # 数据库建表 + 种子数据
├── seed_data.py          # 测试数据生成器
│
├── app/                  # FastAPI 后端
│   ├── main.py           # 应用入口
│   ├── config.py         # Pydantic Settings
│   ├── database.py       # SQLAlchemy 引擎 + 会话
│   ├── models/           # ORM 模型 (9 张表)
│   ├── schemas/          # Pydantic 请求/响应 VO
│   ├── routers/          # API 路由 (8 个模块)
│   ├── services/         # 业务逻辑层
│   ├── security/         # JWT + 鉴权依赖
│   ├── middleware/       # 浏览追踪 + 操作日志 + 邮件
│   ├── background/       # APScheduler + 缓存
│   └── utils/            # IP 提取 + 秒杀管理器
│
└── frontend/             # Vue 3 前端
    ├── vite.config.js    # Vite 配置
    ├── src/
    │   ├── api/          # Axios 封装 + API 函数
    │   ├── router/       # Vue Router 路由 + 守卫
    │   ├── stores/       # Pinia 状态管理
    │   ├── views/        # 11 个页面组件
    │   ├── components/   # 3 个共享组件
    │   └── styles/       # 全局样式
    └── package.json
```

---

## 📖 API 文档

启动后端后自动生成 OpenAPI 交互式文档：

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

### 核心 API 概览

```
POST   /api/user/login          # 用户登录
POST   /api/user/register       # 用户注册
GET    /api/spu/list            # SPU 分页列表
GET    /api/spu/detail/{id}     # SPU 详情（缓存加速）
GET    /api/spu/hot             # 热度排行
GET    /api/spu/similar/{id}    # 看了也看
GET    /api/spu/collaborative/{id} # 协同过滤推荐
POST   /api/order/create        # 创建订单
POST   /api/seckill/{skuId}     # 秒杀
POST   /api/recommend/chat      # AI 推荐对话
GET    /api/admin/reports/*     # 管理员报表
GET    /api/sales/dashboard     # 销售仪表盘
```

---

## 🌐 部署

### 生产构建

```bash
# 前端构建
cd frontend && npm run build
# 输出在 frontend/dist/

# 后端生产运行（Linux）
gunicorn -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:8080 -w 4
```

### Nginx 配置参考

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    root /path/to/frontend/dist;
    try_files $uri $uri/ /index.html;

    # API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📸 截图

> （请自行补充运行截图）

| 页面 | 说明 |
|------|------|
| 🏠 首页 | 横幅 + 分类导航 + 热门 + 全部分页 |
| 📋 商品列表 | 分类/品牌/关键词筛选 + 分页 |
| 📄 商品详情 | SKU 选择 + 相似推荐 + 协同过滤 |
| 🤖 AI 推荐 | 自然语言对话推荐 |
| ⚡ 秒杀 | 商品列表 + 秒杀按钮 |
| 📊 管理员 | 趋势图 + 排行 + 异常 + 人员管理 |
| 🛒 购物车 | 数量调整 + 金额计算 + 结算流程 |

---

## ⚠️ 安全注意事项

- **务必在首次 `git push` 前运行以下命令确保无密钥泄露：**

```bash
# 检查是否还有硬编码密钥
grep -r "sk-" app/config.py
# 检查 .env 是否被 git 跟踪
git status .env
```

- `.env` 文件**绝不能**提交到仓库。使用 `.env.example` 作为模板
- JWT 密钥、DeepSeek API 密钥、SMTP 密码请用强随机字符串替换
- 生产环境请务必更换默认管理员密码 `admin123`

---

## 📄 License

[MIT](LICENSE)

---

## 👨‍💻 作者

**KarlbotK** — [GitHub](https://github.com/KarlbotK)
