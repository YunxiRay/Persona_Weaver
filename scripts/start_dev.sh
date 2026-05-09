#!/usr/bin/env bash
# ============================================================
# Persona Weaver — 本地一键启动 (macOS / Linux / WSL)
# 使用: bash scripts/start_dev.sh
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "=============================================="
echo "  Persona Weaver — 本地一键启动"
echo "=============================================="

# ── 1. Docker 服务 ──
echo ""
echo "[1/4] 启动 Docker 服务 (PostgreSQL + Redis)..."
docker compose up -d

echo "  等待 PostgreSQL 就绪..."
until docker compose exec -T postgres pg_isready -U persona -d persona_weaver &>/dev/null; do
    sleep 2
done
echo "  PostgreSQL 已就绪"

# ── 2. 数据库迁移 ──
echo ""
echo "[2/4] 执行数据库迁移..."
cd backend
poetry run alembic upgrade head || echo "  警告: 迁移失败，继续..."
cd ..

# ── 3. 启动后端 ──
echo ""
echo "[3/4] 启动后端 (http://localhost:8000)..."
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# ── 4. 启动前端 ──
echo ""
echo "[4/4] 启动前端 (http://localhost:5173)..."
cd frontend
npx vite --host &
FRONTEND_PID=$!
cd ..

echo ""
echo "=============================================="
echo "  启动完成！"
echo "=============================================="
echo ""
echo "  后端 API 文档: http://localhost:8000/docs"
echo "  前端页面:     http://localhost:5173"
echo "  LLM 设置:     http://localhost:5173/settings"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo ""

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker compose down; echo '已停止'" EXIT
wait
