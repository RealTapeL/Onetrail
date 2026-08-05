#!/usr/bin/env bash
# ONE TRAIL · 录入杭州经典徒步路线（真实路线，数值为公开资料约值）
# 用法: bash scripts/seed-routes.sh [API_BASE]
#   默认 API_BASE=http://127.0.0.1:8000/api/v1
# 需要后端已启动；使用预设演示账号登录后逐条创建，已存在的同名路线会跳过。
set -euo pipefail

API="${1:-http://127.0.0.1:8000/api/v1}"
: "${ONETRAIL_SEED_EMAIL:?请设置 ONETRAIL_SEED_EMAIL}"
: "${ONETRAIL_SEED_PASSWORD:?请设置 ONETRAIL_SEED_PASSWORD}"
ACCOUNT="$(ONETRAIL_SEED_EMAIL="$ONETRAIL_SEED_EMAIL" ONETRAIL_SEED_PASSWORD="$ONETRAIL_SEED_PASSWORD" python3 -c 'import json,os; print(json.dumps({"email":os.environ["ONETRAIL_SEED_EMAIL"],"password":os.environ["ONETRAIL_SEED_PASSWORD"]}))')"

TOKEN="$(curl -sf -X POST "$API/auth/login" -H 'Content-Type: application/json' -d "$ACCOUNT" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")"

create() {
  local title="$1" json="$2"
  # 同名路线已存在则跳过（简易幂等）
  if curl -sf "$API/routes?query=$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$title")" \
      | python3 -c "import sys,json;d=json.load(sys.stdin);exit(0 if any(i['title']==sys.argv[1] for i in d['items']) else 1)" "$title"; then
    echo "[seed] 已存在，跳过: $title"
    return
  fi
  curl -sf -X POST "$API/routes" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d "$json" > /dev/null && echo "[seed] 已创建: $title"
}

create "九溪十八涧环线" '{
  "title": "九溪十八涧环线",
  "description": "九溪公交站出发，沿九溪烟树溯溪而上至龙井村，溪谷竹林相伴，夏可涉水。雨后石板路湿滑。",
  "region": "浙江省 杭州市 西湖区",
  "start_latitude": 30.2097, "start_longitude": 120.1128,
  "distance_km": 8.0, "elevation_gain_m": 300, "estimated_duration_min": 180,
  "difficulty": "easy", "suitable_for": "新手 · 亲子 · 夏日戏水",
  "tags": [
    {"name": "溪谷", "category": "terrain", "safety_note": "雨后涉水路段湿滑，建议穿防滑徒步鞋"},
    {"name": "瀑布", "category": "scenery"},
    {"name": "竹林", "category": "scenery"}
  ]
}'

create "十里琅珰古道" '{
  "title": "十里琅珰古道",
  "description": "龙井村上行至琅珰岭，沿山脊古道穿行茶园，可下撤梅家坞或云栖竹径。视野开阔，春秋最佳。",
  "region": "浙江省 杭州市 西湖区",
  "start_latitude": 30.2272, "start_longitude": 120.0989,
  "distance_km": 10.0, "elevation_gain_m": 500, "estimated_duration_min": 240,
  "difficulty": "moderate", "suitable_for": "有基础体能的徒步者",
  "tags": [
    {"name": "古道", "category": "terrain"},
    {"name": "茶田", "category": "scenery"},
    {"name": "山脊", "category": "terrain", "safety_note": "山脊段遮阴少，夏季注意补水防晒"}
  ]
}'

create "北高峰灵隐祈福线" '{
  "title": "北高峰灵隐祈福线",
  "description": "灵隐寺旁索道上站下登山步道上北高峰，山顶财神庙观景，可远眺西湖与钱塘江。台阶密集，周末人多。",
  "region": "浙江省 杭州市 西湖区",
  "start_latitude": 30.2405, "start_longitude": 120.0966,
  "distance_km": 6.0, "elevation_gain_m": 350, "estimated_duration_min": 150,
  "difficulty": "moderate", "suitable_for": "新手 · 家庭出行",
  "tags": [
    {"name": "台阶路", "category": "terrain", "safety_note": "连续台阶对膝盖压力大，建议带登山杖"},
    {"name": "观景台", "category": "scenery"},
    {"name": "云海", "category": "scenery"}
  ]
}'

create "宝石山保俶塔环线" '{
  "title": "宝石山保俶塔环线",
  "description": "断桥旁上宝石山，经保俶塔、蛤蟆峰观西湖全景，路程短、爬升小，适合傍晚看日落与夜景。",
  "region": "浙江省 杭州市 西湖区",
  "start_latitude": 30.2631, "start_longitude": 120.1489,
  "distance_km": 3.0, "elevation_gain_m": 100, "estimated_duration_min": 70,
  "difficulty": "easy", "suitable_for": "新手 · 夜游 · 摄影",
  "tags": [
    {"name": "湖景", "category": "scenery"},
    {"name": "夜景", "category": "scenery"},
    {"name": "岩壁", "category": "terrain", "safety_note": "蛤蟆峰岩壁无护栏，拍照勿靠近边缘"}
  ]
}'

create "老和山至北高峰西山游步道" '{
  "title": "老和山至北高峰西山游步道",
  "description": "浙大玉泉校区后老和山起步，沿西山游步道经秦亭山、美女山至北高峰，山脊线连贯，遮阴好。",
  "region": "浙江省 杭州市 西湖区",
  "start_latitude": 30.2734, "start_longitude": 120.1156,
  "distance_km": 7.0, "elevation_gain_m": 400, "estimated_duration_min": 180,
  "difficulty": "moderate", "suitable_for": "日常拉练 · 半日徒步",
  "tags": [
    {"name": "山脊", "category": "terrain"},
    {"name": "林荫", "category": "scenery"}
  ]
}'

create "午潮山国家森林公园环线" '{
  "title": "午潮山国家森林公园环线",
  "description": "小和山上午潮山，原始次生林覆盖，路线长、爬升大，是杭州市区周边少有的硬核拉练线。岔路多，建议结伴。",
  "region": "浙江省 杭州市 余杭区",
  "start_latitude": 30.1833, "start_longitude": 120.0167,
  "distance_km": 12.0, "elevation_gain_m": 800, "estimated_duration_min": 330,
  "difficulty": "hard", "suitable_for": "有徒步经验者 · 拉练",
  "tags": [
    {"name": "原始森林", "category": "scenery"},
    {"name": "野路", "category": "terrain", "safety_note": "岔路多且信号弱，务必结伴并下载离线地图"}
  ]
}'

echo "[seed] 完成。当前路线总数: $(curl -sf "$API/routes?page_size=1" | python3 -c "import sys,json;print(json.load(sys.stdin)['total'])")"
