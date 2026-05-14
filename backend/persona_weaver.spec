# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

block_cipher = None

# Collect static files (frontend dist)
static_dir = Path("static")
static_datas = []
if static_dir.exists():
    for f in static_dir.rglob("*"):
        if f.is_file():
            dest = str(f.relative_to(static_dir).parent)
            static_datas.append((str(f), os.path.join("static", dest)))

# Find jieba dict
jieba_dict = None
for p in sys.path:
    candidate = os.path.join(p, "jieba", "dict.txt")
    if os.path.exists(candidate):
        jieba_dict = (candidate, "jieba")
        break

# Collect seed data (psychology patterns)
seed_datas = []
seed_dir = Path("seed_data")
if seed_dir.exists():
    for f in seed_dir.rglob("*"):
        if f.is_file():
            seed_datas.append((str(f), os.path.join("seed_data", str(f.relative_to(seed_dir).parent))))

datas = static_datas + seed_datas
if jieba_dict:
    datas.append(jieba_dict)

a = Analysis(
    ["run.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "jieba",
        "sqlalchemy.ext.asyncio",
        "aiosqlite",
        "structlog",
        "uvicorn.loops.auto",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
        "openai",
        "httpx",
        "jinja2",
        "webview",
        "webview.platforms.edgechromium",
        "webview.platforms.winforms",
        "webview.js",
        "fastapi.staticfiles",
        "pydantic_settings",
        "huggingface_hub",
      ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "torch",
        "transformers",
        "sentence_transformers",
        "redis",
        "asyncpg",
        "pgvector",
        "alembic",
    ],
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PersonaWeaver",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
