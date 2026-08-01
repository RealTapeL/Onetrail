# ONE TRAIL · 一径 · Web + 移动端原型

Vue 3 + Vite + vue-router 单页应用，**桌面与移动端同构**（同一套路由，按视口切换组件）。
视觉严格还原 Ardot 设计稿（像素复古风：`#0B0B0B` 底 / 荧光绿 `#A3E635` / 0 圆角 / 实体偏移投影）。

## 启动

```bash
cd one-trail-app
npm install
npm run dev        # http://localhost:5173
npm run build      # 产物在 dist/
npm run preview    # 预览构建产物
```

桌面视口（≥820px）渲染桌面版 1440px 屏，移动视口（<820px）渲染移动端页面，路由不变。

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
one-trail-app/
├── docs/
│   ├── API.md               # 后端接口契约（请求/响应 JSON）
│   └── SITEMAP.md           # 束状信息架构与路由表
├── public/images/           # 15 张设计稿导出图
└── src/
    ├── api/mock.js          # ★ 数据层：全部页面数据集中于此，结构对齐 API.md
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

## 后端接管方式（给后端队友）

1. **看契约**：`docs/API.md` 有每个接口的请求/响应 JSON；`docs/SITEMAP.md` 有页面与接口的对应关系。
2. **换数据**：页面数据全部来自 `src/api/mock.js` 的具名导出（brandStats / recommendation / routeDetail / plan / routeLibrary / weatherTip / gearCompare / gapPicks / gearReviews / me）。把这些对象替换为 `fetch('/api/v1/...')` 的返回即可，页面无需改动（换 HTTP 时在页面 setup 中改为 onMounted 拉取）。
3. **联调代理**：在 `vite.config.js` 加 `server.proxy = { '/api': 'http://localhost:8080' }` 指向你的服务。
4. **表单提交**：`postRecommendations(questForm)`（S1/M1 的 PRESS START 调用）即 `POST /recommendations` 的请求体形状。

## 设计还原要点

- 字体：Press Start 2P / Silkscreen / VT323（像素英文）+ Noto Sans SC（中文），Google Fonts CDN
- 实体投影（0 模糊）：白卡 `6px 6px 0 #A3E635`、装备卡 `4px 4px 0 #FFFFFF`（BEST MATCH 为荧光绿）、字段 `3px 3px 0 #0A0A0A`
- 全部 0 圆角；投票条颜色由数据驱动（mock 中 `lime: true/false`）
