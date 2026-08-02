#!/usr/bin/env python3
"""把 tools/decathlon/items.json 导入装备目录。

- match_name 为空的：POST /api/v1/equipment 新增（同名已存在则跳过）
- match_name 指定的：直接 UPDATE 现有装备行的 image_url / source_url
用法: .venv/bin/python scripts/import-decathlon.py（需后端已启动，工作目录任意）
"""

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy import create_engine, text  # noqa: E402
from core.config import get_settings  # noqa: E402

API = "http://127.0.0.1:8000/api/v1"
ACCOUNT = {"email": "admin@onetrail.dev", "password": "admin123456"}


def call(path: str, method: str = "GET", body: dict | None = None, token: str | None = None):
    req = urllib.request.Request(
        f"{API}{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {token}"} if token else {})},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def main() -> None:
    items = json.loads(Path("tools/decathlon/items.json").read_text(encoding="utf-8"))
    token = call("/auth/login", "POST", ACCOUNT)["access_token"]
    existing = {e["name"]: e["id"] for e in call("/equipment")}

    engine = create_engine(get_settings().database_url)
    for it in items:
        payload = it["payload"]
        if it["match_name"]:
            with engine.begin() as conn:
                n = conn.execute(
                    text("UPDATE equipment SET image_url=:img, source_url=:src WHERE name=:name"),
                    {"img": payload["image_url"], "src": payload["source_url"], "name": it["match_name"]},
                ).rowcount
            print(f"[update] {it['match_name']} -> {'已更新' if n else '未找到'}")
        else:
            if payload["name"] in existing:
                print(f"[skip] 已存在: {payload['name']}")
                continue
            call("/equipment", "POST", payload, token)
            print(f"[create] {payload['name']}")


if __name__ == "__main__":
    main()
