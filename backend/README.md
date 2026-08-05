# Onetrail 后端

这是一个不含演示/伪造业务数据的 FastAPI 后端。生产数据库为 PostgreSQL，启动时仅创建空表；路线、装备和评价只会由真实接口请求写入。当前本地 Compose PostgreSQL 映射到主机 `5433`，以避开主机已有的 `5432` 服务。天气和地图能力通过适配器预留，未配置真实服务时会明确返回 `424 Failed Dependency`，不会编造推荐结果。

## 目录约定

`app` 只负责应用总入口（`app/main.py`），不存放任何业务模块。业务代码直接按领域模块放在 `backend` 根目录：

```text
backend/
├── app/                 # FastAPI 总入口、路由装配
├── identity/            # 身份认证与徒步偏好
├── recommendation/      # 智能推荐与外部服务适配边界
├── route_content/       # 路线、标签、评价
├── hiking_history/      # 历史徒步记录与能力画像
├── equipment/           # 装备比选目录
├── platform_services/   # 健康检查、基础平台能力
├── core/                # 配置、安全等跨模块能力
├── database/            # ORM 与会话管理
└── tests/               # 自动化测试
```

## 已实现模块

- `identity`：注册、登录、JWT 鉴权、徒步偏好画像。
- `recommendation`：推荐请求契约、依赖检查、路线适配评分与出发方案接口边界。
- `hiking_history`：记录用户真实完成的徒步，用中位数形成距离、爬升和耗时能力参考。
- `route_content`：路线、标签、路线评价的真实内容 CRUD。
- `equipment`：装备目录、参数、适用场景与评价入口。
- `platform_services`：健康检查、集成状态、基础 API 约定。

暂未实现：约伴与出行协同、个人成长与数据闭环（逻辑图第 4、5 模块）。

## 高德 API 配置

在高德开放平台申请 Web 服务 API Key 后，写入 `.env`：

```env
AMAP_API_BASE_URL=https://restapi.amap.com
AMAP_API_KEY=你的高德Web服务Key
```

当前已接入的高德能力：

- 逆地理编码：根据用户经纬度获取行政区 `adcode`。
- 天气预报：根据 `adcode` 获取目标日期的天气、温度、风力，并推导基础安全提示与“降雨导致的高泥泞风险”。
- 交通规划：查询用户位置到路线起点的驾车、公交/地铁方案。
- 周边 POI：查询路线起点附近的便利店、超市、停车场、公共厕所和游客中心。
- 推荐链路：先定位区域，再查天气；任何高德请求失败都会返回明确错误，不会降级成虚构数据。

高德返回的交通和 POI 数据会直接进入推荐方案；装备建议只从本地真实装备目录读取，目录为空时不会生成商品名称。

推荐接口会综合用户请求、静态偏好和历史记录：

- `POST /api/v1/history`：记录一次真实完成的徒步。
- `GET /api/v1/history`：查看当前用户的历史徒步记录。
- `POST /api/v1/recommendations/plan`：生成天气、路线、交通、补给和装备方案。

推荐评分会对距离、爬升、耗时、难度、天气、泥泞风险、兴趣标签和当前位置分别给出证据，并在 `reasons` 中解释每个推荐原因。没有历史记录时会明确标注使用静态偏好，不会伪造能力数据。

## 启动

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
# 在 .env 中填写可连接的 PostgreSQL DATABASE_URL
python -m uvicorn app.main:app --reload
```

打开 `http://127.0.0.1:8000/docs` 查看并调试接口。

执行测试可安装开发依赖后运行：`pip install -e '.[dev]' && pytest -q`。

## 公网测试前的安全配置

生产环境至少需要设置以下变量，不能沿用 `.env.example` 的占位值：

```env
ENVIRONMENT=production
APP_SECRET_KEY=<使用密码管理器生成的随机 32 位以上密钥>
DATABASE_URL=postgresql+psycopg://<应用账号>:<密码>@<内网数据库地址>:5432/<数据库>?sslmode=require
CORS_ORIGINS=https://<正式前端域名>
ALLOWED_HOSTS=<API域名>
AUTO_CREATE_SCHEMA=false
```

生产环境会关闭 `/docs`、`/redoc` 和 `/openapi.json`，拒绝默认密钥，并使用严格 Host 校验。`docker-compose.yml` 仅用于本机开发，数据库端口已绑定到 `127.0.0.1`，不要将它作为公网数据库部署方式。

应用内限流是单进程保护层；正式多实例部署还必须在 Nginx、云负载均衡或 WAF 上对登录、注册、推荐、高德代理接口配置共享限流，并限制请求体大小。生产部署应通过 HTTPS，数据库仅允许 API 私网访问，并定期轮换密钥、备份和审计数据库账号权限。

## 外部服务接入

在 `recommendation/providers.py` 中实现 `WeatherProvider` 与 `MapProvider` 协议，并通过环境变量提供真实服务地址和密钥。适配器必须将外部响应转换为项目定义的领域模型；不要把第三方响应结构泄漏给前端。
