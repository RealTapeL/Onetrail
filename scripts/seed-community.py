#!/usr/bin/env python3
# ONE TRAIL · 录入全国经典徒步路线与社区评价（真实知名线路，数值为公开资料约值）
# 用法: ../.venv/bin/python scripts/seed-community.py [API_BASE]
#   默认 API_BASE=http://127.0.0.1:8000/api/v1
# 需要后端已启动。幂等：同名路线跳过；已有评价的路线不再重复写入评价。
import json
import os
import sys
import urllib.parse
import urllib.request

API = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/api/v1"
SEED_EMAIL = os.environ.get("ONETRAIL_SEED_EMAIL")
SEED_PASSWORD = os.environ.get("ONETRAIL_SEED_PASSWORD")
if not SEED_EMAIL or not SEED_PASSWORD:
    raise SystemExit("请先设置 ONETRAIL_SEED_EMAIL 和 ONETRAIL_SEED_PASSWORD（仅用于本地种子数据）")
ADMIN = {"email": SEED_EMAIL, "password": SEED_PASSWORD}

# 演示账号（团队成员），用于发布路线与评价
USERS = [
    {"email": "ahao@onetrail.dev", "password": SEED_PASSWORD, "display_name": "阿豪"},
    {"email": "xiaoyu@onetrail.dev", "password": SEED_PASSWORD, "display_name": "小鱼"},
    {"email": "laozhou@onetrail.dev", "password": SEED_PASSWORD, "display_name": "老周"},
    {"email": "lizi@onetrail.dev", "password": SEED_PASSWORD, "display_name": "栗子"},
    {"email": "acan@onetrail.dev", "password": SEED_PASSWORD, "display_name": "阿灿"},
]

# 路线数据：均为公开知名线路，里程/爬升/耗时为公开资料约值（见各条 description 备注）
ROUTES = [
    {
        "title": "徽杭古道（江南村—永来村）",
        "description": "徽商入浙的千年古道，与丝绸之路、茶马古道并称三大古道。从绩溪江南村出发，经江南第一关、下雪堂，抵达制高点蓝天凹（海拔约1050米）的高山草甸，再下山至临安永来村。全程徒步段约15公里（公开资料约值），春季油菜花、秋季层林尽染。雨后石板路湿滑，建议防滑徒步鞋。",
        "region": "安徽省 宣城市 绩溪县",
        "start_latitude": 30.068, "start_longitude": 118.617,
        "distance_km": 15.0, "elevation_gain_m": 800, "estimated_duration_min": 360,
        "difficulty": "moderate", "suitable_for": "新手进阶 · 古道文化 · 春秋两季",
        "tags": [
            {"name": "古道", "category": "terrain", "safety_note": "青石板路雨后湿滑，江南第一关段台阶较陡"},
            {"name": "高山草甸", "category": "scenery"},
            {"name": "徽派古村", "category": "scenery"},
        ],
    },
    {
        "title": "武功山金顶线（沈子村—金顶）",
        "description": "华东最经典的高山草甸线。从沈子村出发一路拔高，穿出云层后沿山脊抵达金顶（白鹤峰，海拔1918.3米），十万亩草甸绵延于海拔1600米之上。全程约15公里、累计爬升约1300米（公开资料约值），建议两天一夜，山顶客栈或帐篷过夜看日出云海。山顶天气多变，防风防雨装备必备。",
        "region": "江西省 萍乡市 芦溪县",
        "start_latitude": 27.456, "start_longitude": 114.173,
        "distance_km": 15.0, "elevation_gain_m": 1300, "estimated_duration_min": 720,
        "difficulty": "moderate", "suitable_for": "两天一夜 · 高山草甸 · 云海日出",
        "tags": [
            {"name": "高山草甸", "category": "scenery"},
            {"name": "云海日出", "category": "scenery"},
            {"name": "山脊线", "category": "terrain", "safety_note": "山顶天气瞬息万变，务必带防风防雨外层；雷雨天避免在山脊逗留"},
        ],
    },
    {
        "title": "麦理浩径第二段（浪茄—北潭凹）",
        "description": "麦理浩径全长100公里、被《国家地理》评为全球最佳徒步径之一，第二段是公认精华：从浪茄出发，串联西湾、咸田湾两片白沙海滩，翻西湾山后抵北潭凹，约13.5公里、需4-5小时（公开资料约值）。西湾、咸田湾有士多可补给。夏季暴晒，全程遮阴少，务必带足饮水。",
        "region": "香港 新界 西贡区",
        "start_latitude": 22.397, "start_longitude": 114.356,
        "distance_km": 13.5, "elevation_gain_m": 500, "estimated_duration_min": 300,
        "difficulty": "moderate", "suitable_for": "海岸风光 · 摄影 · 四季皆宜",
        "tags": [
            {"name": "海岸沙滩", "category": "scenery"},
            {"name": "郊野径", "category": "terrain", "safety_note": "夏季暴晒且遮阴少，人均至少备 1.5L 饮水；留意标距柱 M020-M048"},
        ],
    },
    {
        "title": "东西冲海岸线穿越",
        "description": "深圳最经典的海岸穿越线，被《国家地理杂志》评为中国最美十大徒步路线之一。从东涌村沿海岸线穿至西涌沙滩，全程约7公里、需4-5小时（公开资料约值），一半山路一半礁石海岸，部分礁石段需手脚并用。周末人多，建议早出发。",
        "region": "广东省 深圳市 大鹏新区",
        "start_latitude": 22.483, "start_longitude": 114.552,
        "distance_km": 7.0, "elevation_gain_m": 150, "estimated_duration_min": 300,
        "difficulty": "moderate", "suitable_for": "海岸线 · 团队出行 · 秋冬最佳",
        "tags": [
            {"name": "海岸线", "category": "scenery"},
            {"name": "礁石", "category": "terrain", "safety_note": "礁石湿滑且需攀爬，建议防滑鞋+手套，雨天不宜前往"},
        ],
    },
    {
        "title": "苏州灵白线（灵岩山—白马涧）",
        "description": "苏州人气最高的入门线：南起木渎灵岩山（灵岩山寺），翻大焦山、羊肠岭，北至白马涧龙池景区。全程约7公里、累计爬升约400米（公开资料约值），3-4小时可走完全程。上灵岩寺前为石板路，之后为石砾山径，部分陡坡设有绳索可借力。",
        "region": "江苏省 苏州市 吴中区",
        "start_latitude": 31.267, "start_longitude": 120.518,
        "distance_km": 7.0, "elevation_gain_m": 400, "estimated_duration_min": 210,
        "difficulty": "easy", "suitable_for": "新手 · 周末半日 · 亲子",
        "tags": [
            {"name": "古寺", "category": "scenery"},
            {"name": "山径", "category": "terrain", "safety_note": "陡坡段设有绳索，雨后石砾路滑，建议登山杖"},
        ],
    },
    {
        "title": "无锡军嶂古道A线",
        "description": "军嶂古道入选全国最受欢迎古道，A线为官方标准线：宝界山林公园出发，经笔架山、大山头、幸福水库等至军嶂村，全长约18公里、累计爬升约630米（公开资料约值），海拔均在300米以下但岔路较多，需留意沿途官方路标。中途下撤点与补给点密集，适合一日拉练。",
        "region": "江苏省 无锡市 滨湖区",
        "start_latitude": 31.505, "start_longitude": 120.232,
        "distance_km": 18.0, "elevation_gain_m": 630, "estimated_duration_min": 420,
        "difficulty": "moderate", "suitable_for": "一日拉练 · 古道 · 四季皆宜",
        "tags": [
            {"name": "古道", "category": "terrain", "safety_note": "岔路较多，务必沿官方路标行进，提前下载离线轨迹"},
            {"name": "水库", "category": "scenery"},
            {"name": "密林", "category": "scenery"},
        ],
    },
    {
        "title": "北京三峰连穿（大觉寺—阳台山—妙峰山）",
        "description": "北京户外圈最著名的拉练线，从大觉寺出发，连穿萝卜地北尖（约1140米）、阳台山（1276米）、妙峰山（约1291米）三座千米峰后回到大觉寺。全程约22公里、累计爬升约1700米（公开资料约值），90%以上为山野土路，徒步约10小时。强度大，新手慎入。",
        "region": "北京市 海淀区",
        "start_latitude": 40.059, "start_longitude": 116.100,
        "distance_km": 22.0, "elevation_gain_m": 1700, "estimated_duration_min": 600,
        "difficulty": "hard", "suitable_for": "老驴拉练 · 越野跑 · 大强度一日",
        "tags": [
            {"name": "山脊土路", "category": "terrain", "safety_note": "强度大、耗时长，务必带头灯并预留下撤方案；夏季需备 2L 以上饮水"},
            {"name": "千米峰", "category": "scenery"},
        ],
    },
    {
        "title": "四姑娘山长坪沟（沟口—木骡子）",
        "description": "长坪沟是四姑娘山经典高原徒步线：乘观光车至喇嘛寺后徒步，沿枯树滩、干海子深入，抵达幺妹峰脚下的木骡子高山草甸（海拔约3760米）。单程约12公里，往返约24公里、需9-11小时（公开资料约值），可露营分两天完成。沟内海拔3200米以上，注意高原反应，缓步慢行。",
        "region": "四川省 阿坝州 小金县",
        "start_latitude": 31.005, "start_longitude": 102.898,
        "distance_km": 24.0, "elevation_gain_m": 560, "estimated_duration_min": 660,
        "difficulty": "hard", "suitable_for": "高原徒步 · 雪山草甸 · 可露营",
        "tags": [
            {"name": "雪山", "category": "scenery"},
            {"name": "高山草甸", "category": "scenery"},
            {"name": "高原", "category": "safety", "safety_note": "木骡子海拔约3760米，初上高原者避免剧烈运动，出现高反症状立即下撤"},
        ],
    },
    {
        "title": "泰山红门经典登山线",
        "description": "泰山最经典的徒步登山道：红门出发，经斗母宫、中天门、十八盘、南天门至玉皇顶（海拔1545米），全程约9.5公里、爬升约1300米（公开资料约值），约7000级台阶，普通体力3-6小时登顶。十八盘1633级台阶最考验膝盖，建议登山杖；夜爬看日出需带头灯。",
        "region": "山东省 泰安市 泰山区",
        "start_latitude": 36.255, "start_longitude": 117.107,
        "distance_km": 9.5, "elevation_gain_m": 1350, "estimated_duration_min": 330,
        "difficulty": "moderate", "suitable_for": "五岳打卡 · 日出 · 全程台阶",
        "tags": [
            {"name": "石刻古迹", "category": "scenery"},
            {"name": "台阶", "category": "terrain", "safety_note": "十八盘台阶陡且密，下山伤膝，建议登山杖+护膝；夜爬务必带头灯"},
        ],
    },
    {
        "title": "莫干山国家登山步道环线",
        "description": "莫干山主峰塔山海拔758米，中国四大避暑胜地之一。庾村文化市集出发走环线，串起竹海、剑池、芦花荡与民国别墅群，全程约10公里、累计爬升约560米（公开资料约值），4-5小时走完。植被覆盖率高，夏日清凉；雨后竹林小径湿滑。",
        "region": "浙江省 湖州市 德清县",
        "start_latitude": 30.612, "start_longitude": 119.878,
        "distance_km": 10.0, "elevation_gain_m": 560, "estimated_duration_min": 270,
        "difficulty": "easy", "suitable_for": "避暑 · 竹海 · 民宿度假",
        "tags": [
            {"name": "竹海", "category": "scenery"},
            {"name": "民国别墅", "category": "scenery"},
            {"name": "竹林小径", "category": "terrain", "safety_note": "雨后湿滑，穿防滑鞋；夏季注意防蚊"},
        ],
    },
]

# 社区评价：团队成员基于公开路线特征录入的真实风格反馈
# key 为路线标题（含已有的杭州路线），value 为 (用户序号, 评分, 内容, 印象标签)
REVIEWS = {
    "徽杭古道（江南村—永来村）": [
        (0, 5, "五一走的正穿。江南第一关的石板栈道确实震撼，悬崖上凿出来的路。到蓝天凹豁然开朗，草甸不大但视野极好。下山到永来村那段台阶废膝盖，登山杖救了我。", ["古道", "值得二刷"]),
        (1, 4, "秋天去的，一路溪水相伴不晒。下雪堂有农家可以吃饭补给。整体不难，就是雨后石板有点滑，穿对鞋很重要。", ["秋色", "新手友好"]),
    ],
    "武功山金顶线（沈子村—金顶）": [
        (2, 5, "第一天从沈子村硬拔到金顶，1300米爬升不是开玩笑的，但穿出云层看到草甸那一刻全值了。住山顶客栈，第二天日出云海都赶上了。山顶晚上风巨大，抓绒+硬壳都穿上了。", ["云海", "草甸", "日出"]),
        (3, 4, "草甸是真的辽阔，走不完的山脊线。提醒：金顶客栈旺季要提前订，帐篷营地风大睡不好。水要带够，山上买贵。", ["草甸", "星空"]),
    ],
    "麦理浩径第二段（浪茄—北潭凹）": [
        (1, 5, "西湾和咸田湾的沙真的又白又细，海水清得不像话。翻西湾山那段晒到怀疑人生，1.5L水喝完在咸田湾士多又补了一瓶。标距柱很清楚，一个人走也不慌。", ["海景", "暴晒"]),
    ],
    "东西冲海岸线穿越": [
        (4, 4, "礁石段比想象中刺激，几处要手脚并用，手套很有用。周末人是真多，建议赶早。风景没得说，山海相连一路都出片。", ["海岸线", "礁石"]),
    ],
    "苏州灵白线（灵岩山—白马涧）": [
        (3, 4, "带爸妈走的，半程他们就坐缆车下去了，我一个人走完白马涧。陡坡有绳索借力，不难。周末上午人很多，想清静就工作日去。", ["新手友好", "亲子"]),
    ],
    "无锡军嶂古道A线": [
        (2, 4, "18公里走完正好一天，爬升不大但里程在那，很练耐力。岔路确实多，有一段走神走错了，靠离线轨迹绕回来的。中途下撤点多，新手走半程也行。", ["古道", "拉练"]),
    ],
    "北京三峰连穿（大觉寺—阳台山—妙峰山）": [
        (0, 5, "京圈驴友的毕业考。早上七点大觉寺出发，走完正好天黑。1700米爬升堆在22公里内，最后上妙峰山腿是抖的。全程土路很野，成就感拉满，新手千万别单独来。", ["大强度", "拉练"]),
    ],
    "四姑娘山长坪沟（沟口—木骡子）": [
        (1, 5, "走到木骡子，幺妹峰就在眼前，草甸上牦牛悠闲吃草，值回票价。全程缓坡不陡，但海拔在那，走快了会喘。在木骡子露营一晚，星空银河肉眼可见。", ["雪山", "露营", "星空"]),
        (2, 4, "高原徒步和江浙沪完全两个概念，同样的里程累一倍。建议提前一天到四姑娘山镇适应海拔。沟口到木骡子走不动可以骑马，别硬撑。", ["高反注意", "雪山"]),
    ],
    "泰山红门经典登山线": [
        (3, 4, "夜爬看日出，十一点红门出发四点到顶，头灯必备。十八盘是真的陡，台阶又高又密。山顶凌晨巨冷，租了军大衣。日出云海确实震撼，就是人太多了。", ["日出", "夜爬"]),
    ],
    "莫干山国家登山步道环线": [
        (4, 4, "夏天去的，山里比市区凉快七八度。竹海段很舒服，剑池瀑布水量一般但氛围好。下山在庾村喝咖啡吃碗面，完美的一天。", ["竹海", "避暑"]),
    ],
    # 已有杭州路线补充评价
    "九溪十八涧环线": [
        (1, 5, "杭州夏天的保留项目，一路踩着溪水走，凉快。雨后水流大的时候要脱鞋过溪，带双溯溪鞋体验翻倍。", ["溪谷", "夏日"]),
        (4, 4, "周末人多到炸，想拍照要赶早。龙井村出来可以喝杯茶再走，很舒服的一条线。", ["亲子", "溪谷"]),
    ],
    "十里琅珰古道": [
        (2, 4, "茶园山脊线视野开阔，春天采茶季最漂亮。上下山台阶不少，但都在可接受范围，适合周末半日。", ["茶园", "山脊"]),
    ],
    "北高峰灵隐祈福线": [
        (3, 4, "爬完山顺路去灵隐寺，徒步+祈福一条龙。北高峰台阶比较规整，体力要求不高，老人小孩都能走。", ["祈福", "新手友好"]),
    ],
}


def req(method, path, token=None, payload=None):
    url = API + path
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            body = resp.read().decode()
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def login(account):
    code, data = req("POST", "/auth/login", payload=account)
    if code != 200:
        raise SystemExit(f"[seed] 登录失败 {account['email']}: {code} {data}")
    return data["access_token"]


def ensure_user(user):
    code, _ = req("POST", "/auth/register", payload=user)
    if code == 201:
        print(f"[seed] 注册用户: {user['display_name']}")
    return login({"email": user["email"], "password": user["password"]})


def find_route(title, token):
    code, data = req("GET", f"/routes?query={urllib.parse.quote(title)}", token=token)
    if code != 200:
        return None
    for item in data.get("items", []):
        if item["title"] == title:
            return item
    return None


def main():
    admin_token = login(ADMIN)
    tokens = [ensure_user(u) for u in USERS]

    route_ids = {}
    for route in ROUTES:
        existing = find_route(route["title"], admin_token)
        if existing:
            print(f"[seed] 已存在，跳过: {route['title']}")
            route_ids[route["title"]] = existing["id"]
            continue
        code, data = req("POST", "/routes", token=admin_token, payload=route)
        if code == 201:
            print(f"[seed] 已创建: {route['title']}")
            route_ids[route["title"]] = data["id"]
        else:
            print(f"[seed] 创建失败 {route['title']}: {code} {data}")

    # 已有杭州路线也纳入评价范围
    for title in REVIEWS:
        if title not in route_ids:
            found = find_route(title, admin_token)
            if found:
                route_ids[title] = found["id"]

    for title, reviews in REVIEWS.items():
        rid = route_ids.get(title)
        if not rid:
            print(f"[seed] 找不到路线，跳过评价: {title}")
            continue
        code, existing = req("GET", f"/routes/{rid}/reviews", token=admin_token)
        if code == 200 and existing:
            print(f"[seed] 已有评价，跳过: {title}")
            continue
        for user_idx, rating, content, tags in reviews:
            payload = {"rating": rating, "content": content, "impression_tags": tags}
            code, data = req("POST", f"/routes/{rid}/reviews", token=tokens[user_idx], payload=payload)
            if code == 201:
                print(f"[seed] 已评价: {title} ({USERS[user_idx]['display_name']} {rating}星)")
            else:
                print(f"[seed] 评价失败 {title}: {code} {data}")

    print("[seed] 完成")


if __name__ == "__main__":
    main()
