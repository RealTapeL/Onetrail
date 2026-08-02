#!/usr/bin/env python3
"""迪卡侬官网商品镜像采集（decathlon.com.hk 产品页 __NEXT_DATA__ → 装备目录 JSON）。

用法: python3 tools/decathlon/mirror.py
输出: tools/decathlon/items.json（含新商品 payload 与现有商品的图片/链接更新）
说明: 仅读取公开产品页，图片链接指向迪卡侬官方 CDN，不存储任何虚构数据。
"""

import json
import re
import time
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

# (装备品类, 产品页 URL, 需更新的现有装备名 or None)
PRODUCTS = [
    ("footwear", "https://www.decathlon.com.hk/p/%E7%94%B7%E5%A3%AB%E9%98%B2%E6%B0%B4%E7%99%BB%E5%B1%B1%E9%81%A0%E8%B6%B3%E9%9E%8B-mh100-%E7%81%B0%E8%89%B2-quechua-8503796.html", "迪卡侬 MH100 防水徒步鞋"),
    ("footwear", "https://www.decathlon.com.hk/p/%E7%94%B7%E5%A3%AB%E9%98%B2%E6%B0%B4%E7%99%BB%E5%B1%B1%E9%81%A0%E8%B6%B3%E9%9E%8B-mh500-mid-%E7%81%B0%E8%89%B2-quechua-8618769.html", None),
    ("backpack", "https://www.decathlon.com.hk/p/40l-%E7%99%BB%E5%B1%B1%E8%83%8C%E5%8C%85-mh500-quechua-8786745.html", "迪卡侬 MH500 山地徒步背包 40L"),
    ("backpack", "https://www.decathlon.com.hk/p/22l-%E6%8D%B2%E8%93%8B%E5%BC%8F%E7%99%BB%E5%B1%B1%E9%81%A0%E8%B6%B3%E8%83%8C%E5%8C%85-mh500-%E7%81%B0%E8%89%B2-quechua-8826304.html", None),
    ("tent", "https://www.decathlon.com.hk/p/2%E4%BA%BA2%E7%A7%92%E9%9C%B2%E7%87%9F%E5%BF%AB%E9%96%8B%E5%B8%B3easy-fresh-black-quechua-8553541.html", None),
    ("tent", "https://www.decathlon.com.hk/p/xl%E8%99%9F2%E7%A7%92%E5%BF%AB%E9%96%8B%E9%9C%B2%E7%87%9F%E5%B8%B3%E7%AF%B7fresh-black-3%E4%BA%BA%E7%94%A8-quechua-8503973.html", None),
    ("sleeping_bag", "https://www.decathlon.com.hk/p/0-c-%E5%A4%9A%E6%97%A5%E7%99%BB%E5%B1%B1%E7%9D%A1%E8%A2%8B-mt500-simond-8799901.html", "迪卡侬 MT500 0°C 棉睡袋"),
    ("sleeping_bag", "https://www.decathlon.com.hk/p/5-c-%E5%90%88%E6%88%90%E7%BA%96%E7%B6%AD%E5%A4%9A%E6%97%A5%E7%99%BB%E5%B1%B1%E7%9D%A1%E8%A2%8B-mt500-simond-8799899.html", None),
]

HKD_TO_CNY = 0.92  # 约值，规格中同时保留港币原价

SCENARIOS = {
    "footwear": ["溪谷", "碎石坡", "古道"],
    "backpack": ["露营", "过夜", "山脊"],
    "tent": ["露营", "过夜"],
    "sleeping_bag": ["露营", "过夜"],
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-HK"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_product(html: str) -> dict:
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if not m:
        raise RuntimeError("未找到 __NEXT_DATA__")
    data = json.loads(m.group(1))
    product = data["props"]["pageProps"]["product"]
    images = []
    for item in product.get("items") or []:
        for img in item.get("images") or []:
            if img.get("url") and img["url"] not in images:
                images.append(img["url"])
    if not images:
        for lm in product.get("linkedModels") or []:
            for img in lm.get("images") or []:
                if img.get("url") and img["url"] not in images:
                    images.append(img["url"])
    props = sorted({
        child["name"]
        for group in product.get("aditionnalProperties") or []
        for child in (group.get("childrenIds") or [])
        if child.get("name")
    })
    return {
        "name": product.get("name"),
        "brand": (product.get("brand") or {}).get("name"),
        "model_id": product.get("modelId"),
        "price_hkd": (product.get("price") or {}).get("value"),
        "description": product.get("description"),
        "image_url": images[0] if images else None,
        "properties": props,
    }


def main() -> None:
    out = []
    for category, url, match_name in PRODUCTS:
        print(f"[mirror] 抓取 {url[:80]}…")
        p = parse_product(fetch(url))
        price_hkd = p["price_hkd"]
        specs = {
            "产品编号": p["model_id"],
            "官网港币价": f"HK${price_hkd:g}" if price_hkd else "未标价",
            "特性": "、".join(p["properties"]) if p["properties"] else "见官网",
        }
        if p["description"]:
            specs["官网描述"] = p["description"][:200]
        out.append({
            "category": category,
            "match_name": match_name,
            "payload": {
                "name": f"迪卡侬 {p['name']}",
                "category": category,
                "brand": p["brand"],
                "price_cny": round(price_hkd * HKD_TO_CNY) if price_hkd else None,
                "weight_g": None,
                "specifications": specs,
                "suitable_scenarios": SCENARIOS[category],
                "source_url": url,
                "image_url": p["image_url"],
            },
        })
        print(f"  -> {p['name']} | {p['brand']} | HK${price_hkd} | 图: {'有' if p['image_url'] else '无'}")
        time.sleep(1)
    target = Path(__file__).with_name("items.json")
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[mirror] 已写出 {target}")


if __name__ == "__main__":
    main()
