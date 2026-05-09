@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==============================================
echo   Persona Weaver — 本地一键启动
echo ==============================================
echo.

cd /d "%~dp0\.."

:: ── 1. Docker 服务 ──
echo [1/4] 启动 Docker 服务 (PostgreSQL + Redis)...
docker compose up -d
if %errorlevel% neq 0 (
    echo 错误: Docker 启动失败，请确认 Docker Desktop 已运行
    pause
    exit /b 1
)

echo   等待 PostgreSQL 就绪...
:wait_pg
docker compose exec -T postgres pg_isready -U persona -d persona_weaver >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 2 >nul
    goto wait_pg
)
echo   PostgreSQL 已就绪

:: ── 2. 数据库迁移 ──
echo.
echo [2/4] 执行数据库迁移...
cd backend
call poetry run alembic upgrade head
if %errorlevel% neq 0 (
    echo   警告: 迁移失败，尝试继续...
)
cd ..

:: ── 3. 启动后端 ──
echo.
echo [3/4] 启动后端服务 (FastAPI)...
start "PW-Backend" cmd /c "cd /d %~dp0\..\backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo   后端已在新窗口启动: http://localhost:8000

:: ── 4. 启动前端 ──
echo.
echo [4/4] 启动前端 (Vite)...
start "PW-Frontend" cmd /c "cd /d %~dp0\..\frontend && npx vite --host"
echo   前端已在新窗口启动: http://localhost:5173

echo.
echo ==============================================
echo   启动完成！
echo ==============================================
echo.
echo   后端 API 文档: http://localhost:8000/docs
echo   前端页面:     http://localhost:5173
echo   LLM 设置:     http://localhost:5173/settings
echo.
echo   关闭窗口即可停止服务（Docker 服务需手动停止: docker compose down）
echo.
pause
