# ONE TRAIL · 后端接口契约（v0.2 已对齐）

> 读者：后端开发。本文档从前端原型（Vue 3，`one-trail-app/`）中写死的 mock 数据反推而来。
> 前端 6 屏目前全部是静态数据，接入时逐屏替换为下列接口即可。
> 字段命名、枚举取值都可以商量，本文档是**对齐用的初稿**，不是约束。

---

## 2026-08 联调对齐结果（以此为准）

前端 6 屏已接入真实后端，实际生效的契约与本文档初稿有以下差异：

- **认证**：使用后端已有的邮箱+密码+JWT（`POST /api/v1/auth/register|login`、`GET /api/v1/profile/me`）。前端预设演示账号 `admin@onetrail.dev / admin123456`，首次启动自动注册登录。手机号+验证码未实现。
- **推荐**：`POST /api/v1/recommendations/plan` 同步返回完整结果（Top 5 `routes` + `alternates` 备选 + 每路线 `risk_notes`/交通/补给/装备建议），不落库，因此没有 `GET /recommendations/{id}`；S2/S4 由前端共享状态驱动。
- **plans 模块未实现**：S4 的交通/补给/装备清单直接来自推荐响应；checklist 勾选为前端本地状态。时间线与海拔剖面因无真实数据源，保留设计稿静态展示并已在界面标注"示意/演示"。
- **路线库**：`GET /api/v1/routes` 响应为 `{total, page, items}`（分页参数 `page/page_size`），条目含 `level`（难度映射 easy→1/moderate→2/hard→4/expert→5）与 `average_rating`；筛选参数 `query/tag/level_min/level_max/max_distance_km/crowd`。
- **路线详情**：`GET /api/v1/routes/{id}` 含 `suitable_for`、`average_rating`、`review_count`、`impression_stats`（气质投票计数，前端换算百分比）；评价列表单独走 `GET /api/v1/routes/{id}/reviews`；verdict 由评分聚合前端推导。
- **新增**：`GET /api/v1/meta/brand-stats`（真实统计）、`GET /api/v1/meta/weather-tip?latitude&longitude`（高德天气胶囊，未配置返回 424）、`GET /api/v1/equipment/reviews/summary`（装备评价摘要）、路线收藏 `POST/DELETE /api/v1/routes/{id}/favorite`。
- **装备比选**：S6 直接消费 `GET /api/v1/equipment?category=`（含评分聚合），无单独 `/gear/*` 端点；GAP PICKS 为前端按预算从真实目录筛选。
- 错误格式沿用 FastAPI 默认 `{ "detail": "…" }`，未实现契约中的 `{code, message}`。

以下为初稿原文，仅作设计意图参考。

---

- 基础约定：`BASE_URL /api/v1`，JSON 编码，时间用 ISO 8601 或 `HH:mm` 字符串（见各字段备注）
- 鉴权：`Authorization: Bearer <token>`（登录/注册除外）
- 错误格式：`{ "code": "ROUTE_NOT_FOUND", "message": "路线不存在" }`

---

## 0. 屏 ↔ 接口对照表

| 屏 | 页面 | 需要的接口 |
|---|---|---|
| 01 需求输入 | S1Home | `GET /meta/brand-stats`、`POST /recommendations` |
| 02 智能推荐 | S2Routes | `GET /recommendations/{id}` |
| 03 路线详情 | S3Detail | `GET /routes/{id}`（含评价/投票/判定） |
| 04 执行助手 | S4Exec | `POST /plans`、`GET /plans/{id}`、`PATCH /plans/{id}/checklist` |
| 05 路线库 | S5Library | `GET /routes`（搜索/筛选/分页）、`GET /meta/weather-tip` |
| 06 装备比选 | S6Gear | `GET /gear/compare`、`GET /gear/gap-picks`、`GET /gear/reviews-summary` |
| 全局 | HudNav | `POST /auth/register`、`POST /auth/login`、`GET /users/me` |

---

## 1. 鉴权与用户

### POST /auth/register
```json
// 请求
{ "phone": "13800000000", "code": "123456", "nickname": "阿绿" }
// 响应
{ "token": "jwt…", "user": { "id": "u_001", "nickname": "阿绿", "level": 3, "levelTitle": "HIKER" } }
```

### POST /auth/login
同上结构响应。

### GET /users/me
```json
{ "id": "u_001", "nickname": "阿绿", "level": 3, "levelTitle": "HIKER",
  "fitnessLevel": 3, "city": "杭州", "ownedGear": ["登山鞋", "背包", "登山杖"] }
```
> 导航右上角「LV.3 HIKER」来自 `level + levelTitle`；S1 表单「已有装备」默认值来自 `ownedGear`。

---

## 2. 首页（S1）

### GET /meta/brand-stats
Hero 底部三个品牌数字。
```json
{ "routeCount": 12847, "hikerCount": 86000, "cityCount": 342 }
```

### POST /recommendations
「开始生成路线」按钮提交。请求体即 S1 表单的 7 个字段：
```json
// 请求
{
  "dateRange": { "start": "2026-05-02", "end": "2026-05-04", "nights": 2 },
  "location": { "city": "杭州", "district": "西湖区", "useCurrentPosition": true },
  "party": { "adults": 2, "type": "FRIENDS" },
  "budgetPerPerson": { "min": 300, "max": 500 },
  "fitnessLevel": 3,
  "interests": ["瀑布", "竹林"],
  "ownedGear": ["登山鞋", "背包", "登山杖"]
}
// 响应
{ "recommendationId": "rec_20260502_001" }
```
> `party.type` 枚举：`SOLO / FRIENDS / FAMILY / COUPLE`；`fitnessLevel` 1-5。

---

## 3. 推荐结果（S2）

### GET /recommendations/{recommendationId}
```json
{
  "id": "rec_20260502_001",
  "conditionSummary": "本周末 · 杭州 · 2 人 · ¥500 · 体能 Lv.3",
  "top": [
    {
      "rank": 1,
      "routeId": "r_jiuxi",
      "name": "九溪十八涧 · 环线",
      "coverImage": "/images/routes/jiuxi-cover.webp",
      "matchScore": 96,
      "distanceKm": 9.5, "elevationGainM": 320, "durationH": 4,
      "weather": { "condition": "晴", "temperatureC": 18 },
      "reasons": ["体能 Lv.3 匹配，爬升平缓友好", "竹林溪谷景观，命中你的兴趣", "沿途 3 处补给点，风险可控"],
      "riskWarning": "雨后溪石湿滑，建议防滑徒步鞋",
      "tags": ["溪谷", "竹林", "新手友好"]
    },
    { "rank": 2, "routeId": "r_huihang", "matchScore": 89, "…": "…" },
    { "rank": 3, "routeId": "r_damingshan", "matchScore": 82, "…": "…" }
  ],
  "alternatives": [
    { "routeId": "r_luniao", "name": "鸬鸟山温泉线", "summary": "轻松休闲 · 6.0KM · 温泉补给", "thumb": "/images/routes/luniao-thumb.webp" },
    { "routeId": "r_jingshan", "name": "径山古道", "summary": "文化禅意 · 7.8KM · 新手友好", "thumb": "/images/routes/jingshan-thumb.webp" }
  ]
}
```
> `matchScore` 0-100 整数，前端直接拼 `%`；`reasons` 固定 3 条展示效果最好。

---

## 4. 路线详情（S3）

### GET /routes/{routeId}
一次返回整屏数据（投票、评价、判定都内嵌，前端不额外发请求）：
```json
{
  "id": "r_jiuxi",
  "name": "九溪十八涧 · 环线",
  "stats": { "distanceKm": 9.5, "elevationGainM": 320, "durationH": 4, "difficultyLevel": 2 },
  "media": { "coverImage": "/images/routes/jiuxi-cover.webp", "videoPreviewUrl": null, "videoDurationSec": 42 },
  "terrain": {
    "tags": [
      { "label": "垭口", "warning": false },
      { "label": "溪谷", "warning": false },
      { "label": "碎石坡", "warning": false },
      { "label": "涉水 ×2 处", "warning": true },
      { "label": "陡坡 ×1 段", "warning": true }
    ],
    "safetyTip": "涉水路段雨后水位上涨，建议上午通过；碎石坡路段注意防滑。"
  },
  "reviews": [
    { "author": "阿绿", "rating": 5, "visitedAt": "上周走过", "content": "溪水清澈，竹林段特别出片，带爸妈走也完全没问题。" },
    { "author": "山雾散人", "rating": 4, "visitedAt": "3 月走过", "content": "雨后涉水段水有点深，早点出发人少体验更好。" }
  ],
  "vibeVote": {
    "items": [
      { "label": "出片", "percent": 86 },
      { "label": "自然体验", "percent": 92 },
      { "label": "故事性", "percent": 64 },
      { "label": "体能挑战", "percent": 41 }
    ]
  },
  "suitableFor": ["新手友好", "亲子出行", "摄影爱好者"],
  "verdict": { "worth": true, "text": "值得去", "voteCount": 1284 }
}
```
> 前端投票条颜色规则：`percent ≥ 60` 显示荧光绿，否则街机黄——后端只给数值即可。
> `verdict.worth` 由社区投票聚合，`voteCount` 用于「基于 N 票社区共识投票」。

---

## 5. 出行计划（S4）

### POST /plans
S3「加入出行计划」触发。
```json
// 请求
{ "routeId": "r_jiuxi", "date": "2026-05-02", "partySize": 2 }
// 响应
{ "planId": "p_001" }
```

### GET /plans/{planId}
```json
{
  "id": "p_001",
  "title": "九溪十八涧环线 · 5月2日出发 · 2 人",
  "transit": [
    { "type": "TRAIN", "line": "高铁 · 上海虹桥 → 杭州东", "detail": "07:15 – 08:06 · 二等座 ¥73" },
    { "type": "METRO", "line": "地铁 1 号线 · 杭州东 → 龙翔桥", "detail": "25 分钟 · ¥4" },
    { "type": "BUS", "line": "公交 4 路 · 龙翔桥 → 九溪站", "detail": "30 分钟 · ¥2 · 步行 800M 至入口" }
  ],
  "transitTip": "返程末班公交 18:30，注意下山时间",
  "timeline": [
    { "time": "08:30", "event": "九溪入口集合", "remindable": true },
    { "time": "09:00", "event": "出发 · 溪谷竹林段", "remindable": true },
    { "time": "12:00", "event": "龙井村 · 午餐补给", "remindable": true },
    { "time": "15:30", "event": "杨梅岭 · 到达终点", "remindable": true },
    { "time": "17:00", "event": "返程", "remindable": true }
  ],
  "supplyPoints": [
    { "code": "S1", "name": "龙井村", "services": ["午餐", "补水"], "kmMark": 4.2 },
    { "code": "S2", "name": "理安寺", "services": ["补水", "休息"], "kmMark": 6.8 },
    { "code": "S3", "name": "杨梅岭", "services": ["终点补给"], "kmMark": 9.5 }
  ],
  "checklist": [
    { "item": "登山鞋", "owned": true,  "required": true },
    { "item": "背包 20L", "owned": true,  "required": true },
    { "item": "2L 饮水", "owned": false, "required": true },
    { "item": "雨具", "owned": false, "required": true },
    { "item": "头灯", "owned": false, "required": true },
    { "item": "能量食品", "owned": false, "required": true }
  ],
  "elevationProfile": {
    "points": [45, 80, 70, 150, 130, 230, 190, 260, 210, 240],
    "maxAltitudeM": 420, "totalClimbM": 320, "waterCrossings": 2, "supplyCount": 3,
    "markers": [
      { "label": "入口 45M", "ratioX": 0.0 },
      { "label": "S1 龙井村", "ratioX": 0.35 },
      { "label": "S2 理安寺", "ratioX": 0.59 },
      { "label": "S3 杨梅岭", "ratioX": 0.81 },
      { "label": "最高 420M", "ratioX": 0.92 }
    ]
  }
}
```
> `transit.type` 枚举：`TRAIN / METRO / BUS / FLIGHT / COACH / TAXI`，前端按枚举画像素图标。
> `elevationProfile.points` 是归一化前的海拔采样数组，前端画阶梯图；`ratioX` 0-1，标记横向位置。
> 缺口件数 = `checklist` 中 `owned=false` 的数量（前端现在写死"缺口 4 件"）。

### PATCH /plans/{planId}/checklist
勾选/取消装备：
```json
// 请求
{ "item": "雨具", "owned": true }
// 响应：更新后的 checklist 数组
```

---

## 6. 路线库（S5）

### GET /routes
搜索 + 筛选 + 分页：
```
GET /routes?keyword=九溪&scene=竹林&levelMin=1&levelMax=5&maxDistanceKm=15&crowd=新手&page=1&pageSize=12
```
```json
{
  "total": 12847,
  "page": 1,
  "items": [
    { "id": "r_jiuxi", "name": "九溪十八涧 · 环线", "coverImage": "/images/routes/jiuxi-cover.webp",
      "distanceKm": 9.5, "elevationGainM": 320, "difficultyLevel": 2, "rating": 4.8 },
    { "id": "r_huihang", "name": "徽杭古道 · 精华段", "…": "…" }
  ]
}
```
> `scene` 枚举来自设计稿：`瀑布 / 古道 / 竹林 / 云海 / 星空`（可多选则逗号分隔）；`crowd`：`新手 / 亲子 / 硬核`。

### GET /meta/weather-tip
搜索栏右侧的天气胶囊：
```json
{ "text": "本周晴好 · 适合溪谷竹林线" }
```

---

## 7. 装备比选（S6）

### GET /gear/compare
按品类 + 路线场景返回 3 个对比款：
```
GET /gear/compare?category=徒步鞋&routeId=r_jiuxi
```
```json
{
  "category": "徒步鞋",
  "categories": ["背包", "徒步鞋", "帐篷", "睡袋"],
  "contextSummary": "已按「九溪环线 · 溪谷涉水」生成建议",
  "items": [
    { "id": "g_crispi", "name": "CRISPI Monaco GTX", "image": "/images/gear/crispi.webp",
      "price": 1899, "weightKg": 1.4, "waterproof": "GTX 全袜套",
      "suitTags": ["轻装", "古道"], "rating": 4.8, "bestMatch": false },
    { "id": "g_scarpa", "name": "SCARPA 冈仁波齐", "image": "/images/gear/scarpa.webp",
      "price": 1299, "weightKg": 1.2, "waterproof": "GTX 全袜套",
      "suitTags": ["溪谷", "涉水路线"], "rating": 4.7, "bestMatch": true },
    { "id": "g_kailas", "name": "凯乐石 征途", "image": "/images/gear/kailas.webp",
      "price": 699, "weightKg": 1.1, "waterproof": "防泼水涂层",
      "suitTags": ["新手", "轻徒步"], "rating": 4.5, "bestMatch": false }
  ]
}
```
> `bestMatch=true` 的卡前端渲染荧光绿投影 + 「最适合本路线 · BEST MATCH」徽章；每张卡规格表前端目前按 `价格/重量/防水/适合/评分` 5 行展示。

### GET /gear/gap-picks
按路线与预算，补给 S4 清单里的缺口：
```
GET /gear/gap-picks?routeId=r_jiuxi&budgetMax=500
```
```json
{
  "title": "缺口补给建议 · GAP PICKS — 按你的路线与预算生成",
  "items": [
    { "id": "g_raincoat", "category": "雨具", "name": "三峰出 15D 雨衣", "sellingPoints": ["防暴雨", "仅 180G", "收纳巴掌大"], "price": 129 },
    { "id": "g_headlamp", "category": "头灯", "name": "奈特科尔 NU25", "sellingPoints": ["400 流明", "仅 56G", "USB-C 充电"], "price": 168 },
    { "id": "g_waterbag", "category": "饮水", "name": "驼峰 2L 水袋", "sellingPoints": ["快拆吸嘴", "适配 20L 背包"], "price": 149 }
  ]
}
```

### GET /gear/reviews-summary
底部真实评价条：
```json
{ "totalCount": 1203,
  "sample": { "quote": "冈仁波齐走溪谷两天，鞋里没进水。", "gearId": "g_scarpa" } }
```

---

## 8. 前端对接备注（给后端也方便联调）

1. **dev 代理**：前端 Vite 已留 `server` 配置，联调时加一行即可免 CORS：
   ```js
   // vite.config.js
   server: { port: 5173, proxy: { '/api': 'http://localhost:8080' } }
   ```
2. **图片**：目前 15 张 webp 是设计稿导出图，放在 `public/images/`。正式环境建议后端返 CDN URL，前端 `<img :src>` 直接替换。
3. **前端写死、需要接数据的位置**（按文件）：
   - `S1Home.vue` → brand-stats、recommendations 提交
   - `S2Routes.vue` → recommendations 详情
   - `S3Detail.vue` → routes 详情（一屏一个接口）
   - `S4Exec.vue` → plans 详情 + checklist PATCH
   - `S5Library.vue` → routes 列表 + weather-tip
   - `S6Gear.vue` → gear 三组接口
4. **暂不需要后端**：slogan、像素山插画、导航高亮、屏间跳转，全部前端逻辑。
5. 枚举和错误码若要调整，改本文档后通知前端同步即可。
