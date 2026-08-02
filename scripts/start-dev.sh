#!/usr/bin/env bash
# ONE TRAIL · 一键启动前后端（含基础服务）
# 用法: bash scripts/start-dev.sh
#   前台运行并聚合输出日志，Ctrl+C 会同时停止后端与前端（数据库容器保留）。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"

# 1. 基础服务（PostgreSQL）
bash "$ROOT/scripts/start-services.sh"

# 2. 后端 uvicorn（端口 8000；应用日志由后端 logger 写入 logs/backend.log）
if curl -sf -m 2 http://127.0.0.1:8000/health > /dev/null 2>&1; then
  echo "[dev] 8000 端口已有健康后端在运行，跳过后端启动"
  BACKEND_PID=""
else
  echo "[dev] 启动后端 → http://0.0.0.0:8000"
  (cd "$ROOT/backend" && exec "$ROOT/.venv/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port 8000) \
    > "$LOG_DIR/backend-console.log" 2>&1 &
  BACKEND_PID=$!
fi

# 3. 前端 vite（端口 5173；控制台输出写入 logs/frontend-console.log）
if curl -sf -m 2 -o /dev/null http://127.0.0.1:5173/; then
  echo "[dev] 5173 端口已有前端在运行，跳过前端启动"
  FRONTEND_PID=""
else
  echo "[dev] 启动前端 → http://0.0.0.0:5173"
  (cd "$ROOT/frontend" && exec npx vite --no-open) > "$LOG_DIR/frontend-console.log" 2>&1 &
  FRONTEND_PID=$!
fi

cleanup() {
  echo
  echo "[dev] 停止前后端进程（PostgreSQL 容器保留运行）..."
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup INT TERM

LAN_IP="$(ip -4 addr show scope global | awk '/inet /{print $2}' | cut -d/ -f1 | head -1)"
cat <<EOF

[dev] 全部就绪：
  前端        http://localhost:5173   局域网  http://${LAN_IP:-<本机IP>}:5173
  后端 API    http://localhost:8000/docs
  日志目录    logs/  （backend.log 后端+数据库错误，frontend.log 前端上报，*-console.log 进程输出）

按 Ctrl+C 停止前后端。
EOF

# 聚合跟踪日志文件（进程控制台输出），保持脚本前台运行
tail -n +1 -F "$LOG_DIR/backend-console.log" "$LOG_DIR/frontend-console.log" 2>/dev/null &
TAIL_PID=$!
trap 'kill "$TAIL_PID" 2>/dev/null; cleanup' INT TERM

wait
