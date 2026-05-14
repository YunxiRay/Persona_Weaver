# Persona Weaver Windows .exe 一键构建脚本
# 前置条件: Python 3.11-3.13, Node.js 18+, pnpm
# 注意: Python 3.14 暂不支持 pywebview/pythonnet；
#       如果检测到 3.14，会自动使用 3.13 进行 PyInstaller 打包

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

# ── 选择 Python 版本 ──
$PYTHON = (Get-Command python -ErrorAction SilentlyContinue).Source
$PY_VER = & $PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"

if ($PY_VER -eq "3.14") {
    Write-Host "[!] 当前 Python $PY_VER 不支持 pywebview，尝试使用 Python 3.13..." -ForegroundColor Yellow
    $PY313 = "C:\Users\Yunxi Rany\AppData\Local\Programs\Python\Python313\python.exe"
    if (Test-Path $PY313) {
        $PYTHON = $PY313
        Write-Host "  使用: $PYTHON" -ForegroundColor Green
    } else {
        Write-Host "  未找到 Python 3.13，将跳过 pywebview（使用浏览器模式）" -ForegroundColor Yellow
    }
}

# ── 1. 构建前端 ──
Write-Host "[1/4] 构建前端..." -ForegroundColor Cyan
Set-Location "$ROOT\frontend"
pnpm install --frozen-lockfile
pnpm build

# ── 2. 复制前端 dist → backend/static ──
Write-Host "[2/4] 复制前端静态文件..." -ForegroundColor Cyan
$staticDir = "$ROOT\backend\static"
if (Test-Path $staticDir) { Remove-Item -Recurse -Force $staticDir }
Copy-Item -Recurse "$ROOT\frontend\dist" $staticDir
Write-Host "  已复制到 $staticDir" -ForegroundColor Green

# ── 3. 安装后端依赖 ──
Write-Host "[3/5] 安装后端依赖..." -ForegroundColor Cyan
Set-Location "$ROOT\backend"
& $PYTHON -m pip install fastapi "uvicorn[standard]" pydantic pydantic-settings "sqlalchemy[asyncio]" aiosqlite httpx openai "python-jose[cryptography]" python-multipart structlog jieba jinja2

# 尝试安装 pywebview（Python <3.14 才支持）
$PY_VER = & $PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$PY_VER -lt [version]"3.14") {
    Write-Host "[4/5] 安装 pywebview + pywin32..." -ForegroundColor Cyan
    & $PYTHON -m pip install pywebview pywin32
} else {
    Write-Host "[4/5] 跳过 pywebview (Python $PY_VER 不支持)" -ForegroundColor Yellow
}

# ── 5. PyInstaller 打包 ──
Write-Host "[5/5] PyInstaller 打包..." -ForegroundColor Cyan
& $PYTHON -m pip install pyinstaller
& $PYTHON -m PyInstaller --clean persona_weaver.spec

Write-Host ""
Write-Host "构建完成! 输出: $ROOT\backend\dist\PersonaWeaver.exe" -ForegroundColor Green
Write-Host "预计大小: 30-50 MB" -ForegroundColor Yellow
