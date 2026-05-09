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

### 1. 克隆项目

```bash
git clone https://github.com/YunxiRay/Persona_Weaver.git
cd Persona_Weaver
```

### 2. 启动基础设施

```bash
docker compose -f docker/docker-compose.yml up -d
```

这将启动 PostgreSQL 16（含 pgvector 扩展）和 Redis 7。

### 3. 配置后端

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入你的开发者测试 LLM Key（可选，调试用）
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

API 文档自动生成在 `http://localhost:8000/docs`。

### 4. 配置前端

```bash
cd frontend
pnpm install
cp .env.example .env
pnpm dev
```

前端运行在 `http://localhost:5173`。

### 5. 配置 LLM

打开浏览器访问 `http://localhost:5173/settings`，选择你的 LLM 厂商并填入 API Key，点击"测试连接"验证通过后即可开始对话。

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
├── backend/           # FastAPI 后端
├── frontend/          # React 前端
├── docker/            # Docker Compose 配置
├── nginx/             # Nginx 反向代理配置
├── scripts/           # 工具脚本
├── docs/              # 文档
├── .github/           # CI/CD 配置
├── .gitignore
├── LICENSE
└── README.md
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
