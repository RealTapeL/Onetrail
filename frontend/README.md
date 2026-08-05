# ONE TRAIL · 一径 · Web + 移动端原型

Vue 3 + Vite + vue-router 单页应用，**桌面与移动端同构**（同一套路由，按视口切换组件）。
视觉严格还原 Ardot 设计稿（像素复古风：`#0B0B0B` 底 / 荧光绿 `#A3E635` / 0 圆角 / 实体偏移投影）。

## 启动

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173（/api 代理到 127.0.0.1:8000 后端）
npm run build      # 产物在 dist/
npm run preview    # 预览构建产物
```

部署到静态服务器时，必须在构建阶段配置后端 API 地址，否则浏览器会把 `POST /api/v1/auth/login` 发给只支持静态文件的服务器并返回 501：

```bash
cp .env.production.example .env.production
# 将 VITE_API_BASE 改为正式 HTTPS 后端地址
npm run build
```

前端静态服务器只负责返回网页文件；`/api` 请求必须指向 FastAPI 服务或由 Nginx/Caddy 反向代理到 FastAPI，不能由 `python -m http.server` 处理。

桌面视口（≥820px）渲染桌面版 1440px 屏，移动视口（<820px）渲染移动端页面，路由不变。
前端已接入真实后端：需先启动 backend（uvicorn，8000 端口），详见根目录 README。

## 路由（对齐 docs/SITEMAP.md 束状 IA）

| 路由 | 束 | 桌面组件 | 移动组件 | 页面 |
|---|---|---|---|---|
| `/plan` | 规划 | S1Home | MPlan | 需求输入（真实表单） |
| `/plan/results` | 规划 | S2Routes | MPlanResults | 推荐结果 Top3（下层页） |
| `/routes` | 路线库 | S5Library | MRoutes | 搜索·筛选·列表 |
| `/routes/:id` | 路线库 | S3Detail | MRouteDetail | 路线详情（下层页） |
| `/trip/current` | 行程 | S4Exec | MTrip | 执行助手 |
| `/gear` | 装备 | S6Gear | MGear | 装备比选 |

跨束旅程：需求输入 ─生成→ 推荐结果 ─点卡→ 路线详情 ─加入计划→ 执行助手 ─缺口→ 装备比选。

## 工程结构

```
frontend/
├── docs/
│   ├── API.md               # 后端接口契约（请求/响应 JSON，v0.2 已对齐实现）
│   └── SITEMAP.md           # 束状信息架构与路由表
├── public/images/           # 15 张设计稿导出图
└── src/
    ├── api/http.js          # fetch 封装（/api/v1、Bearer、会话 ensureSession）
    ├── api/index.js         # ★ 数据层：全部页面数据的真实接口 loader
    ├── router.js            # 路由 + byDevice 桌面/移动组件切换
    ├── composables/useIsMobile.js
    ├── styles/main.css      # 设计 token
    ├── components/
    │   ├── HudNav.vue       # Web 顶部导航（对应 Ardot 组件 6:4）
    │   ├── ui/Btn.vue       # 共享按钮（对应 Ardot Button ×3）
    │   ├── ui/Chip.vue      # 共享标签（对应 Ardot Chip ×2）
    │   ├── S1Home.vue … S6Gear.vue        # 桌面 6 屏
    │   └── mobile/
    │       ├── TabBar.vue   # 底部 Tab（对应 Ardot 组件 6:28）
    │       ├── MHeader.vue / BackHeader.vue
    │       └── MPlan.vue … MGear.vue      # 移动 6 屏
    └── App.vue / main.js
```

## 后端接入现状

页面数据已全部切换到真实接口（`src/api/index.js`），原 mock 数据层已删除：

- **会话**：`/login` 页邮箱+密码登录/注册（`api/http.js` 的 `loginWith`/`registerWith`），token 存 localStorage；路由守卫拦截未登录访问，导航栏可退出登录。
- **S1/M1 需求输入** → `POST /api/v1/recommendations/plan`（体能等级映射为距离/爬升硬限制；兴趣写入偏好画像；已有装备按名称匹配目录 id）。
- **S2/M6 推荐结果** ← 共享状态 `state.recommendation`（Top3 + 备选 + 风险提示）。
- **S5/M2 路线库** → `GET /api/v1/routes`（关键词/景观标签筛选）；天气胶囊 → `GET /api/v1/meta/weather-tip`（浏览器定位，未授权时不显示）。
- **S3/M5 路线详情** → `GET /api/v1/routes/{id}` + `/reviews`；收藏 → `POST/DELETE /favorite`。
- **S4/M3 执行助手** ← 由选中推荐路线生成（交通/补给来自高德；时间线与海拔剖面为演示，界面已标注）。
- **S6/M4 装备比选** → `GET /api/v1/equipment`（GAP PICKS 按 S1 预算过滤）+ `/equipment/reviews/summary`。

联调代理已配置：`vite.config.js` 的 `server.proxy = { '/api': 'http://127.0.0.1:8000' }`。

## 设计还原要点

- 字体：Press Start 2P / Silkscreen / VT323（像素英文）+ Noto Sans SC（中文），Google Fonts CDN
- 实体投影（0 模糊）：白卡 `6px 6px 0 #A3E635`、装备卡 `4px 4px 0 #FFFFFF`（BEST MATCH 为荧光绿）、字段 `3px 3px 0 #0A0A0A`
- 全部 0 圆角；投票条颜色由数据驱动（印象标签占比 ≥60% 为荧光绿，否则琥珀色）
