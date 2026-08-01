# Onetrail

Onetrail 不是单纯的轨迹记录工具，而是一个帮助用户在出发前完成徒步决策的平台：

> 这条路适不适合我、值不值得去、怎么去和带什么？

当前仓库以可运行的后端为主，核心亮点是“智能线路推荐”主链路。

## 当前能力

- 用户注册、登录与 JWT 鉴权
- 用户徒步偏好：距离、爬升、耗时、难度、兴趣标签
- 历史徒步记录与能力画像
- 路线库、路线标签、地形/安全信息与评价
- 路线可信档案：适合人群、评价聚合（平均分/数量）、气质印象投票统计
- 路线关键词搜索（标题/描述/区域）与收藏
- 高德逆地理编码与天气预报
- 高德驾车、公交/地铁路线规划
- 路线起点周边补给点查询
- 结合天气、泥泞风险、路线数据和用户能力的可解释推荐（Top 5 + 备选路线 + 风险提示）
- 基于真实装备目录生成装备参考（支持预算与已有装备过滤）
- 装备真实评价与评分聚合
- PostgreSQL 数据库与 Docker Compose 本地环境

没有配置或没有返回真实数据时，接口会明确返回依赖错误或空结果，不会填充演示路线、天气、装备或评价。

## 技术栈

- Python 3.11+
- FastAPI + Uvicorn
- Pydantic
- SQLAlchemy 2.0
- PostgreSQL + psycopg
- JWT + Argon2 密码哈希
- 高德 Web Service API
- pytest

## 目录结构

```text
Onetrail/
├── backend/
│   ├── app/                 # FastAPI 总入口与路由装配
│   ├── identity/            # 身份、登录、用户偏好
│   ├── hiking_history/      # 历史徒步记录与能力画像
│   ├── recommendation/     # 推荐引擎、高德适配器
│   ├── route_content/       # 路线、标签、评价、收藏
│   ├── equipment/           # 装备目录、评价与建议
│   ├── platform_services/   # 健康检查、集成状态、平台统计
│   ├── core/                # 配置与安全能力
│   ├── database/            # 数据库引擎与会话
│   └── tests/               # 自动化测试
├── frontend/                # Vue 3 + Vite 原型（6 屏已接入后端）
└── docs/                    # 产品逻辑图
```

## 前端启动

前端是 Vue 3 + Vite 原型，6 个页面已接入后端真实数据（预设演示账号自动登录）：

```bash
# 1. 先启动后端（见上文，默认 127.0.0.1:8000）
# 2. 启动前端开发服务器（/api 已代理到后端）
cd frontend
npm ci
npm run dev
```

打开 <http://localhost:5173>。首次启动会自动注册并登录演示账号 `admin@onetrail.dev`。

## 本地启动

### 1. 启动 PostgreSQL

```bash
cd backend
docker compose up -d
```

默认容器映射到本机 `5433`，避免与本机已有的 PostgreSQL `5432` 冲突。

### 2. 创建 Python 环境并安装依赖

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

在 `.env` 中填写高德 Web 服务 API Key：

```env
AMAP_API_BASE_URL=https://restapi.amap.com
AMAP_API_KEY=你的高德Web服务Key
```

### 4. 启动 API

```bash
python -m uvicorn app.main:app --reload
```

接口文档：<http://127.0.0.1:8000/docs>

## 智能线路推荐

推荐入口：

```http
POST /api/v1/recommendations/plan
```

推荐流程：

```text
出行日期 + 当前经纬度
    ↓
高德逆地理编码 → adcode
    ↓
高德天气预报 → 温度、风力、天气现象、泥泞风险
    ↓
路线硬筛选 → 距离、爬升、耗时
    ↓
可解释评分 → 难度、历史能力、兴趣、天气、位置
    ↓
高德交通规划 + 周边补给点
    ↓
真实装备目录 → 装备建议
```

历史徒步记录接口：

```http
POST /api/v1/history
GET  /api/v1/history
```

没有历史记录时，系统会使用用户静态偏好，并在响应中明确说明能力样本数为 0。

## 测试

测试通过 `tests/conftest.py` 自动隔离：默认使用临时 SQLite 数据库、每个用例前重置表结构，并强制外部服务处于未配置状态（不读取本机 `.env` 中的高德 Key）：

```bash
python -m pytest -q
```

生产和本地应用默认使用 PostgreSQL。注意：应用靠 `create_all` 建表（无 Alembic），schema 演进后**已有的本地数据库需要删除重建**才能看到新列和新表。

## 当前未实现范围

以下模块暂未纳入当前开发分支：

- 约伴、同行点、拼车与临时聊天
- 徒步日历、成就墙和完整个人成长闭环
- Alembic 生产迁移脚本
- 图片/视频对象存储与内容审核后台
