# CLAUDE.md — Persona Weaver 项目配置

## 项目概述

Persona Weaver (人格织梦者) 是一款开源的 AI 心理人格分析 Agent。通过模拟真实的心理咨询体验，利用多轮递进式对话和贝叶斯推理引擎，在深度叙事中还原用户最真实的人格底色。

- **技术栈**: Python 3.11 + FastAPI (后端) / React 18 + Vite + TypeScript + TailwindCSS (前端)
- **数据库**: PostgreSQL 16 + pgvector / Redis 7
- **部署**: Docker Compose 单机部署

## 强制规则

### 1. 开发日志

**每次对话开始时**，必须先读取 `开发日志.md` 了解当前项目状态和已完成的任务。

**每次对话结束时**，必须更新 `开发日志.md`：
- 记录本轮完成的所有任务和具体产出
- 追加在文件末尾，**绝不覆盖已有内容**
- 使用 `## YYYY-MM-DD — 任务名称` 格式作为日期标题
- 每个任务以 `### 任务 X.X — 任务名称 ✅` 格式记录
- 列出具体完成内容（文件、功能、关键决策）
- 如果完成了一个 Phase 的全部任务，添加阶段总结

### 2. 代码规范

- **后端**: 遵循 FastAPI 最佳实践，使用 async/await，pydantic 做数据校验，structlog 做日志
- **前端**: React 18 + TypeScript 严格模式，TailwindCSS 原子化样式，组件放在 `components/` 下对应子目录
- **安全**: 绝对不在代码中硬编码 API Key，不提交 `.env` 文件，pre-commit hook 自动检测密钥
- **注释**: 只写必要的注释说明 WHY，不写 WHAT
- **测试**：每完成某项必要功能，必须提供完善的测试方案，并执行测试并将测试结果写入测试报告，测试报告保存到'测试报告.md'.

### 3. Git 规则

- 不主动 commit，除非用户明确要求
- 提交前确保 pre-commit 检查通过
- Commit message 使用中文，格式：`[Phase X] 简要描述`
- 不提交 `.env`、`node_modules`、`__pycache__`、`*.log` 等
- 不 force push，不跳过 hooks

### 4. 项目上下文

- **当前 Phase**: Phase 1（项目脚手架）— 已完成
- **下一步 Phase**: Phase 2（数据层）
- **开发文档**: `项目开发计划.md`（任务拆分）、`人格织梦者 (Persona Weaver) 项目全量开发文档.md`（架构细节）
- **API Key 策略**: 项目代码不内置任何 API Key，用户通过前端设置页自行配置 LLM 厂商
- **开发测试模型**: DeepSeek V4 Pro（开发者本地 `.env` 注入，不上传仓库）
- **目标用户**: 国内中文互联网用户（C 端为主）
- **语言**: 仅简体中文

## 目录结构

```
persona-weaver/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── api/       # REST + WebSocket 端点
│   │   ├── core/      # 配置、日志、安全
│   │   ├── engine/    # 叙事引导、情感反馈、推理评分
│   │   ├── llm/       # LLM Provider 抽象层
│   │   ├── models/    # SQLAlchemy 模型
│   │   ├── schemas/   # Pydantic Schema
│   │   └── services/  # 业务逻辑层
│   ├── migrations/    # Alembic 迁移
│   └── tests/
├── frontend/          # React 前端
│   ├── src/
│   │   ├── pages/     # 路由页面
│   │   ├── components/# UI 组件
│   │   ├── hooks/     # 自定义 Hooks
│   │   ├── stores/    # Zustand 状态
│   │   └── lib/       # 工具函数
│   └── nginx/
├── scripts/           # 工具脚本
├── docker-compose.yml
└── 开发日志.md        # 开发进度记录
```
