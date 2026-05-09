# Persona Weaver（人格织梦者）

> 在对话中发现自己 — 一款开源的 AI 心理人格分析 Agent。

Persona Weaver 模拟真实的心理咨询体验，通过递进式对话引导、多维度交叉验证和贝叶斯推理引擎，在自然叙事中还原用户最真实的人格底色。**本工具不是问卷，而是一场四阶段的深度对话。**

---

## 特性

- **四阶段叙事引导**：破冰 → 探索 → 对峙 → 收束，模拟专业心理咨询的渐进逻辑
- **贝叶斯推理引擎**：随语料累积实时更新人格维度置信度，而非一次性打分
- **动态跃迁机制**：置信度达标时自动跳过不必要的阶段，缩短高配合用户的对话时长
- **安全锚点与熔断**：检测到高风险情绪时自动降级，内置心理援助信息
- **五维深度报告**：性格骨架 / 认知地图 / 语言素描 / 趣味标签 / 心理医生寄语
- **用户自配 LLM**：项目不内置任何 API Key，用户通过设置页接入自己的 LLM 账号

---

## 快速开始

### 前置依赖

| 软件 | 最低版本 | 说明 |
| :--- | :--- | :--- |
| Python | 3.11+ | 推荐 pyenv 管理版本 |
| Node.js | 20 LTS | 前端运行时 |
| pnpm | 9.x | 前端包管理 |
| Docker Desktop | 26+ | 运行 PostgreSQL + Redis |
| Poetry | 1.8+ | Python 依赖管理 |

### 一键启动（推荐）

```bash
git clone https://github.com/YunxiRay/Persona_Weaver.git
cd Persona_Weaver

# 首次运行：安装依赖
bash scripts/setup_dev.sh

# 之后每次启动：
# Windows: 双击 scripts\start_dev.bat
# macOS / Linux / WSL: bash scripts/start_dev.sh
```

脚本会自动启动 Docker（PG + Redis）、运行数据库迁移、启动后端（8000）和前端（5173）。

### 手动启动

#### 1. 启动基础设施

```bash
docker compose up -d
```

#### 2. 配置后端

```bash
cd backend
cp .env.example .env
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

API 文档: `http://localhost:8000/docs`

#### 3. 配置前端

```bash
cd frontend
pnpm install
pnpm dev
```

前端: `http://localhost:5173`

### 配置 LLM

打开浏览器访问 `http://localhost:5173/settings`，选择 LLM 厂商并填入 API Key，点击"测试连接"验证通过后即可开始对话。

---

## 支持的 LLM 厂商

| Provider | 默认模型 | API Key 获取 |
| :--- | :--- | :--- |
| DeepSeek | `deepseek-chat` | [platform.deepseek.com](https://platform.deepseek.com) |
| 通义千问 | `qwen-plus` | [dashscope.aliyun.com](https://dashscope.aliyun.com) |
| 智谱 GLM | `glm-4` | [open.bigmodel.cn](https://open.bigmodel.cn) |
| Moonshot (Kimi) | `moonshot-v1-8k` | [platform.moonshot.cn](https://platform.moonshot.cn) |
| OpenAI 兼容 | 自定义 | 支持 Ollama / vLLM / 任意兼容接口 |

---

## 技术栈

| 层次 | 选型 |
| :--- | :--- |
| 后端框架 | Python 3.11 + FastAPI |
| 数据库 | PostgreSQL 16 + pgvector |
| 缓存 | Redis 7 |
| 嵌入模型 | bge-large-zh (HuggingFace 本地部署) |
| 前端 | React 18 + Vite + TypeScript |
| UI | TailwindCSS + shadcn/ui |
| 图表 | ECharts |
| 部署 | Docker Compose + Nginx |

---

## 项目结构

```
Persona_Weaver/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/              # REST + WebSocket 端点
│   │   ├── core/             # 配置、安全、中间件、数据库
│   │   ├── engine/           # 叙事引导、情感反馈、推理评分
│   │   ├── llm/              # LLM Provider 抽象层
│   │   ├── models/           # SQLAlchemy 模型
│   │   ├── schemas/          # Pydantic Schema
│   │   └── services/         # 业务逻辑层
│   ├── migrations/           # Alembic 数据库迁移
│   ├── tests/                # 后端测试 (pytest)
│   └── Dockerfile
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/       # UI 组件（chat/report/settings）
│   │   ├── hooks/            # 自定义 Hooks（useWebSocket）
│   │   ├── lib/              # 工具（API 客户端、WebSocket 客户端）
│   │   ├── pages/            # 路由页面（Home/Chat/Report/Settings/Privacy/Terms）
│   │   ├── stores/           # Zustand 状态管理
│   │   └── __tests__/        # 前端测试 (vitest)
│   └── Dockerfile
├── scripts/                  # 工具脚本
│   ├── setup_dev.sh          # 开发环境一键初始化
│   ├── seed_prompts.py       # 提示词种子数据
│   └── deploy.sh             # 生产环境一键部署
├── docker-compose.yml        # 开发环境 Docker Compose
├── docker-compose.prod.yml   # 生产环境 Docker Compose
├── .env.production.example   # 生产环境变量模板
├── .github/                  # Issue/PR 模板
├── .gitignore
├── LICENSE
└── README.md
```

---

## 生产环境部署

### 前置条件

- Docker Engine 20.10+ 和 Docker Compose v2+
- 一台 Linux 服务器（推荐 Ubuntu 22.04 / CentOS 8+，2 核 4G 以上）
- 域名（可选，用于 SSL）

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/YunxiRay/Persona_Weaver.git
cd Persona_Weaver

# 2. 配置环境变量
cp .env.production.example .env.production
# 编辑 .env.production，修改所有密码和 SECRET_KEY

# 3. 执行部署
bash scripts/deploy.sh
```

部署完成后访问 `http://<服务器IP>` 即可使用。

### SSL 配置（推荐）

生产环境建议配置 HTTPS。在 `frontend/nginx/default.conf` 中添加 SSL 证书配置，或使用 Nginx Proxy Manager / Caddy 作为前置反向代理。

```nginx
# 在 frontend/nginx/default.conf 中添加:
listen 443 ssl;
ssl_certificate     /etc/nginx/ssl/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/privkey.pem;
```

### 云服务器开通 checklist

1. 安全组规则：开放 80/443 端口，**关闭** 5432（PostgreSQL）和 6379（Redis）公网访问
2. 域名 DNS 解析到服务器 IP（如有域名）
3. 安装 Docker：`curl -fsSL https://get.docker.com | bash`
4. 配置防火墙：`ufw allow 80/tcp && ufw allow 443/tcp`
5. 设置 swap（2G 以下内存服务器）：`fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile`

### 常用运维命令

```bash
# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f backend

# 重启服务
docker compose -f docker-compose.prod.yml restart

# 数据库迁移
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 备份数据库
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U persona persona_weaver > backup.sql

# 停止服务
docker compose -f docker-compose.prod.yml down
```

---

## 贡献

欢迎提交 Issue 和 Pull Request。在提交 PR 之前请确保：

1. 代码通过 Ruff lint 和 MyPy 类型检查
2. 新增功能包含测试
3. **绝不提交任何 API Key 或密钥文件**

---

## 免责声明

本工具提供的报告仅为心理类型倾向参考，**不能替代专业心理诊断或治疗**。用户需年满 16 周岁。对话数据默认匿名存储，仅用于当次分析，用户可随时清除。

---

## License

[MIT](LICENSE)
