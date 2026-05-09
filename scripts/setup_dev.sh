#!/usr/bin/env bash
set -euo pipefail

echo "=== Persona Weaver 开发环境初始化 ==="

# 1. Start Docker services
echo "[1/4] 启动 Docker 服务 (PostgreSQL + Redis)..."
docker compose up -d

# 2. Install backend dependencies
echo "[2/4] 安装 Python 依赖..."
cd backend
cp -n .env.example .env 2>/dev/null || true
pip install poetry==1.8.2
poetry install --with dev

# 3. Install frontend dependencies
echo "[3/4] 安装 Node.js 依赖..."
cd ../frontend
cp -n .env.example .env 2>/dev/null || true
corepack enable
corepack prepare pnpm@9 --activate
pnpm install

# 4. Verify
echo "[4/4] 验证环境..."
docker compose ps
echo ""
echo "=== 初始化完成 ==="
echo "后端: cd backend && poetry run uvicorn app.main:app --reload"
echo "前端: cd frontend && pnpm dev"
echo "API 文档: http://localhost:8000/docs"
echo "前端页面: http://localhost:5173"
