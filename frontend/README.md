# ONE TRAIL · 一径 · Vue 原型

将 Ardot 画布上的 6 屏设计稿**严格还原**为 Vue 3 + Vite 单页应用（纯前端，无后端）。
还原依据：`batch_read` 抓取的节点级尺寸 / 配色 / 文案 / 字体 / 描边 / 实体投影实测值。

## 启动

```bash
cd one-trail-app
npm install
npm run dev        # http://localhost:5173
npm run build      # 产物在 dist/
npm run preview    # 预览构建产物 http://localhost:4173
```

也可用 `?screen=s1…s6` 直达某屏，例如 `http://localhost:5173/?screen=s3`。

## 给后端的交接

**`docs/API.md` 是接口契约**——从 6 屏的 mock 数据反推的 REST 接口草案（屏 ↔ 接口对照表、请求/响应 JSON、枚举取值、联调代理配置）。后端按它实现，前端逐屏把写死的数据替换成接口返回即可。

## 6 屏（每屏严格 1440×960）

| 屏 | 组件 | 内容 |
|---|---|---|
| 01 需求输入 | `S1Home.vue` | HUD 导航 + Hero（slogan/三问/品牌数据/像素山）+ 白色需求表单（7 字段 + PRESS START） |
| 02 智能推荐 | `S2Routes.vue` | 3 张白色路线卡（TOP1-3，6px 荧光绿投影，照片/匹配度/理由/风险条）+ 备选路线面板 |
| 03 路线详情 | `S3Detail.vue` | 左：预览图/Stats HUD/地形标签/评价；右：白卡（气质投票 2 绿 2 黄、适合人群、值得去判定、CTA） |
| 04 执行助手 | `S4Exec.vue` | 三列：大交通（像素图标）/ 时间线（铃铛）/ 补给与装备清单；海拔剖面 SVG；4 个操作按钮 |
| 05 路线库 | `S5Library.vue` | 搜索框（荧光绿投影）+ 景观筛选 chips + 6 张路线卡 |
| 06 装备比选 | `S6Gear.vue` | 分类 tabs + 3 张装备卡（BEST MATCH 荧光绿投影）+ GAP PICKS + 真实评价条 |

屏间联动：开始生成路线→02、TOP1 卡→03、加入出行计划→04、去装备比选→06、导航菜单互通。

## 设计 token（`src/styles/main.css`）

- 底色 `#0B0B0B` / 面板 `#161616` / 描边 `#2E2E2E`
- 荧光绿 `#A3E635` / 街机黄 `#FFD028` / 风险红 `#D32F2F`（底 `#FFF3F3` 边 `#FF5252`）
- 浅色面 `#FFFFFF` / 表单底 `#FAFAF7` / 投票轨道 `#EAEAE4`
- 字体：Press Start 2P / Silkscreen / VT323（像素英文）+ Noto Sans SC（中文 400/500/700/900），Google Fonts CDN
- 实体投影（0 模糊）：白卡 `6px 6px 0 #A3E635`、字段 `3px 3px 0 #0A0A0A`、装备卡 `4px 4px 0 #FFFFFF`（BEST MATCH 卡为荧光绿）
- 全部 0 圆角

## 图片

`public/images/` 15 张 webp，由 Ardot `export_nodes` 从设计稿导出（路线照片、装备图、缩略图）。
