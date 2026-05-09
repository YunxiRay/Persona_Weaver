#!/usr/bin/env bash
# ============================================================
# Persona Weaver — 生产环境一键部署脚本
# 使用: bash scripts/deploy.sh
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "=============================================="
echo "  Persona Weaver — 生产环境部署"
echo "=============================================="

# ── 1. 检查依赖 ──
echo ""
echo "[1/5] 检查依赖..."

if ! command -v docker &>/dev/null; then
    echo "错误: 未安装 Docker，请先安装 Docker Engine 20.10+"
    exit 1
fi

DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+' | head -1)
echo "  Docker: $DOCKER_VERSION"

if ! command -v docker compose &>/dev/null; then
    echo "错误: 未安装 Docker Compose，请先安装 Docker Compose v2+"
    exit 1
fi

COMPOSE_VERSION=$(docker compose version --short)
echo "  Docker Compose: $COMPOSE_VERSION"

# ── 2. 检查环境变量 ──
echo ""
echo "[2/5] 检查环境变量..."

ENV_FILE=""
if [ -f ".env.production" ]; then
    ENV_FILE="--env-file .env.production"
    echo "  已找到 .env.production"
else
    echo "  警告: 未找到 .env.production，使用 .env.production.example 作为模板"
    echo "  请编辑 .env.production 填入实际密码和密钥后重新运行"
    cp -n .env.production.example .env.production 2>/dev/null || true
    echo "  已创建 .env.production，请编辑后重新运行本脚本"
    exit 1
fi

# ── 3. 拉取最新代码 ──
echo ""
echo "[3/5] 拉取最新代码..."

if [ -d ".git" ]; then
    git pull origin main 2>/dev/null || echo "  (跳过 git pull，使用当前代码)"
else
    echo "  (非 git 仓库，使用当前代码)"
fi

# ── 4. 构建并启动 ──
echo ""
echo "[4/5] 构建 Docker 镜像并启动服务..."

docker compose -f docker-compose.prod.yml $ENV_FILE build --pull
docker compose -f docker-compose.prod.yml $ENV_FILE up -d

# ── 5. 运行数据库迁移 ──
echo ""
echo "[5/5] 运行数据库迁移..."

# 等待 backend 就绪
echo "  等待 backend 启动..."
for i in $(seq 1 30); do
    if docker compose -f docker-compose.prod.yml $ENV_FILE ps backend | grep -q "healthy\|Up"; then
        break
    fi
    sleep 2
done

# 在 backend 容器中运行 alembic upgrade
docker compose -f docker-compose.prod.yml $ENV_FILE exec -T backend alembic upgrade head 2>/dev/null || \
    echo "  注意: 数据库迁移可能需要手动执行: docker compose -f docker-compose.prod.yml exec backend alembic upgrade head"

# ── 完成 ──
echo ""
echo "=============================================="
echo "  部署完成！"
echo "=============================================="
echo ""
echo "  服务状态:"
docker compose -f docker-compose.prod.yml $ENV_FILE ps
echo ""
echo "  访问地址: http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip')"
echo ""
echo "  常用命令:"
echo "    查看日志:  docker compose -f docker-compose.prod.yml logs -f"
echo "    重启服务:  docker compose -f docker-compose.prod.yml restart"
echo "    停止服务:  docker compose -f docker-compose.prod.yml down"
echo "    数据库迁移: docker compose -f docker-compose.prod.yml exec backend alembic upgrade head"
echo ""
