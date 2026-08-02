#!/usr/bin/env bash
# ONE TRAIL · 录入经典徒步装备目录（真实产品，价格/重量为公开资料约值）
# 用法: bash scripts/seed-equipment.sh [API_BASE]
#   默认 API_BASE=http://127.0.0.1:8000/api/v1
# 需要后端已启动；使用预设演示账号登录后逐条创建，同名装备会跳过。
set -euo pipefail

API="${1:-http://127.0.0.1:8000/api/v1}"
ACCOUNT='{"email":"admin@onetrail.dev","password":"admin123456"}'

TOKEN="$(curl -sf -X POST "$API/auth/login" -H 'Content-Type: application/json' -d "$ACCOUNT" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")"

exists() {
  curl -sf "$API/equipment" | python3 -c "import sys,json;exit(0 if any(i['name']==sys.argv[1] for i in json.load(sys.stdin)) else 1)" "$1"
}

create() {
  local name="$1" json="$2"
  if exists "$name"; then
    echo "[seed] 已存在，跳过: $name"
    return
  fi
  curl -sf -X POST "$API/equipment" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d "$json" > /dev/null && echo "[seed] 已创建: $name"
}

review() {
  local name="$1" json="$2"
  local id
  id="$(curl -sf "$API/equipment" | python3 -c "import sys,json;print(next((i['id'] for i in json.load(sys.stdin) if i['name']==sys.argv[1]), ''))" "$name")"
  [[ -z "$id" ]] && return
  # 已有评价则跳过
  curl -sf "$API/equipment/$id/reviews" | python3 -c "import sys,json;exit(0 if json.load(sys.stdin) else 1)" && { echo "[seed] 已有评价，跳过: $name"; return; }
  curl -sf -X POST "$API/equipment/$id/reviews" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d "$json" > /dev/null && echo "[seed] 已评价: $name"
}

# ---- 背包 ----
create "迪卡侬 MH500 山地徒步背包 40L" '{
  "name": "迪卡侬 MH500 山地徒步背包 40L", "category": "backpack", "brand": "DECATHLON",
  "price_cny": 299, "weight_g": 1150,
  "specifications": {"容量": "40L", "防水": "防泼水（附防雨罩）", "背负": "网架透气"},
  "suitable_scenarios": ["一日徒步", "古道", "山脊"]
}'
create "格里高利 ZULU 35L 登山背包" '{
  "name": "格里高利 ZULU 35L 登山背包", "category": "backpack", "brand": "GREGORY",
  "price_cny": 1099, "weight_g": 1350,
  "specifications": {"容量": "35L", "防水": "防泼水", "背负": "FreeFloat 悬浮背负"},
  "suitable_scenarios": ["一日徒步", "重装拉练", "山脊"]
}'
create "三峰出 轨迹 45+10L 轻量化背包" '{
  "name": "三峰出 轨迹 45+10L 轻量化背包", "category": "backpack", "brand": "三峰出",
  "price_cny": 799, "weight_g": 980,
  "specifications": {"容量": "45+10L", "防水": "无（需防雨罩）", "背负": "轻量框架"},
  "suitable_scenarios": ["露营", "过夜", "古道"]
}'

# ---- 徒步鞋 ----
create "迪卡侬 MH100 防水徒步鞋" '{
  "name": "迪卡侬 MH100 防水徒步鞋", "category": "footwear", "brand": "DECATHLON",
  "price_cny": 299, "weight_g": 780,
  "specifications": {"防水": "防水透气膜", "中底": "EVA 缓震", "大底": "CrossContact 抓地"},
  "suitable_scenarios": ["溪谷", "竹林", "一日徒步", "古道"]
}'
create "凯乐石 FUGA EX2 越野跑鞋" '{
  "name": "凯乐石 FUGA EX2 越野跑鞋", "category": "footwear", "brand": "KAILAS",
  "price_cny": 899, "weight_g": 560,
  "specifications": {"防水": "不防水（快干）", "中底": "EVA+碳板", "大底": "Vibram Megagrip"},
  "suitable_scenarios": ["山脊", "碎石坡", "拉练"]
}'
create "SCARPA 莫林 GTX 中帮登山鞋" '{
  "name": "SCARPA 莫林 GTX 中帮登山鞋", "category": "footwear", "brand": "SCARPA",
  "price_cny": 1599, "weight_g": 1100,
  "specifications": {"防水": "GORE-TEX", "中底": "双密度 EVA", "大底": "Vibram"},
  "suitable_scenarios": ["涉水", "碎石坡", "重装", "陡坡"]
}'

# ---- 帐篷 ----
create "牧高笛 冷山2 双人三季帐" '{
  "name": "牧高笛 冷山2 双人三季帐", "category": "tent", "brand": "MOBI GARDEN",
  "price_cny": 499, "weight_g": 2400,
  "specifications": {"人数": "2人", "防水": "外帐 PU3000mm", "结构": "双层铝杆"},
  "suitable_scenarios": ["露营", "过夜"]
}'
create "挪客 云尚2 超轻双人帐" '{
  "name": "挪客 云尚2 超轻双人帐", "category": "tent", "brand": "Naturehike",
  "price_cny": 899, "weight_g": 1500,
  "specifications": {"人数": "2人", "防水": "外帐 20D 涂硅 PU4000mm", "结构": "双层铝杆"},
  "suitable_scenarios": ["露营", "过夜", "轻量化"]
}'

# ---- 睡袋 ----
create "黑冰 G700 羽绒睡袋" '{
  "name": "黑冰 G700 羽绒睡袋", "category": "sleeping_bag", "brand": "BLACKICE",
  "price_cny": 1099, "weight_g": 1020,
  "specifications": {"温标": "舒适 -5°C", "填充": "700FP 白鹅绒", "防水": "面料防泼水"},
  "suitable_scenarios": ["露营", "过夜", "高海拔"]
}'
create "迪卡侬 MT500 0°C 棉睡袋" '{
  "name": "迪卡侬 MT500 0°C 棉睡袋", "category": "sleeping_bag", "brand": "DECATHLON",
  "price_cny": 249, "weight_g": 1550,
  "specifications": {"温标": "舒适 0°C", "填充": "中空棉", "防水": "无"},
  "suitable_scenarios": ["露营", "过夜"]
}'

# ---- 真实评价（驱动评分聚合与评价摘要） ----
review "迪卡侬 MH100 防水徒步鞋" '{"rating": 5, "content": "走九溪溪谷两天，鞋里没进水，湿滑石板抓地也稳。"}'
review "凯乐石 FUGA EX2 越野跑鞋" '{"rating": 4, "content": "十里琅珰全程很轻快，就是不防水，雨天慎选。"}'
review "迪卡侬 MH500 山地徒步背包 40L" '{"rating": 4, "content": "一日线装两人份水和路餐刚好，背板透气不闷。"}'
review "黑冰 G700 羽绒睡袋" '{"rating": 5, "content": "山顶过夜 0 度上下没觉得冷，压缩后很小。"}'

echo "[seed] 完成。装备总数: $(curl -sf "$API/equipment" | python3 -c "import sys,json;print(len(json.load(sys.stdin)))")"
