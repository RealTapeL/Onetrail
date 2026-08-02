#!/usr/bin/env bash
# ONE TRAIL · 一键启动基础服务（PostgreSQL 容器）
# 用法: bash scripts/start-services.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[services] 启动 PostgreSQL 容器..."
docker compose -f "$ROOT/backend/docker-compose.yml" up -d postgres

echo "[services] 等待数据库就绪..."
for i in $(seq 1 30); do
  status="$(docker inspect -f '{{.State.Health.Status}}' backend-postgres-1 2>/dev/null || echo missing)"
  if [[ "$status" == "healthy" ]]; then
    echo "[services] PostgreSQL 已就绪（容器 backend-postgres-1，端口 5433）"
    exit 0
  fi
  sleep 1
done

echo "[services] 等待超时，数据库未就绪，请执行 docker logs backend-postgres-1 查看原因" >&2
exit 1
