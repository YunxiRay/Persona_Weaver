# Persona Weaver（人格织梦者）

> 在对话中发现自己 — 一款开源的 AI 心理人格分析桌面应用。

Persona Weaver 模拟真实的心理咨询体验，通过递进式对话引导、贝叶斯推理引擎和 **RAG 心理学知识库检索**，在自然叙事中还原用户最真实的人格底色。**不是问卷，而是一场四阶段的深度对话。**

---

## 特性

- **四阶段叙事引导**：破冰 → 探索 → 对峙 → 收束，模拟专业心理咨询的渐进逻辑
- **贝叶斯推理引擎**：随语料累积实时更新人格维度置信度，支持时间衰减防过拟合
- **RAG 心理学知识库**：内建 50 条专业心理学模式，实时向量检索匹配，为 LLM 分析提供专业知识参照
- **动态跃迁机制**：置信度达标 + MBTI 稳定后自动进入收束阶段
- **安全锚点与熔断**：检测到高风险情绪时自动降级，内置心理援助信息
- **五维深度报告**：性格骨架 / 认知地图 / 语言素描 / SBTI 趣味标签 / 心理医生寄语
- **用户自配 LLM**：项目不内置任何 API Key，用户通过设置页接入自己的 LLM 账号
- **桌面原生体验**：PyInstaller 打包为独立 .exe，pywebview 原生窗口，无需安装浏览器

---

## 快速开始

### 下载运行（推荐）

从 [Releases](../../releases) 页面下载最新 `PersonaWeaver.exe`，双击运行。程序自动打开桌面窗口。

首次启动会自动下载嵌入模型（约 1.3GB）到 `~/.persona-weaver/models/`，仅需一次。模型下载在后台进行，不影响正常使用。

### 配置 LLM

启动后在设置页面选择 LLM 厂商并填入 API Key，点击"测试连接"验证通过后即可开始对话。

> 建议使用一个全新的 API Key，避免在其他 AI 应用中的聊天记录被当作上下文影响对话质量。

### 从源码构建

**前置依赖**: Python 3.11-3.13, Node.js 20+, pnpm 9+, Poetry

```bash
# 1. 安装后端依赖
cd backend
poetry install

# 2. 构建前端
cd ../frontend
pnpm install && pnpm build

# 3. 复制静态文件
Copy-Item -Recurse frontend/dist backend/static

# 4. 构建 .exe
cd ../backend
python -m PyInstaller --clean persona_weaver.spec
# 输出: backend/dist/PersonaWeaver.exe
```

### 开发模式

```bash
# 终端 1 — 后端
cd backend
poetry run python run.py --no-gui

# 终端 2 — 前端 (可选，后端已托管 static/)
cd frontend
pnpm dev
```

---

## 支持的 LLM 厂商

| Provider | 默认模型 | API Key 获取 |
|:---|:---|:---|
| DeepSeek | `deepseek-chat` | [platform.deepseek.com](https://platform.deepseek.com) |
| 通义千问 | `qwen-plus` | [dashscope.aliyun.com](https://dashscope.aliyun.com) |
| 智谱 GLM | `glm-4` | [open.bigmodel.cn](https://open.bigmodel.cn) |
| Moonshot (Kimi) | `moonshot-v1-8k` | [platform.moonshot.cn](https://platform.moonshot.cn) |
| OpenAI 兼容 | 自定义 | 支持 Ollama / vLLM / 任意兼容接口 |

---

## 技术栈

| 层次 | 选型 |
|:---|:---|
| 后端框架 | Python 3.13 + FastAPI |
| 数据库 | SQLite (aiosqlite) |
| 嵌入模型 | bge-large-zh-v1.5（首次启动自动下载） |
| 向量检索 | numpy 内存索引（dot product 余弦相似度） |
| 推理引擎 | Beta 分布贝叶斯更新 + 时间衰减 |
| 打包 | PyInstaller + pywebview |
| 前端 | React 18 + Vite + TypeScript |
| UI | TailwindCSS |
| 图表 | ECharts |
| 分词 | jieba |

---

## 项目结构

```
Persona_Weaver/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/          # REST 端点 (config/session/report/pattern/data/debug)
│   │   │   └── ws/              # WebSocket 对话通道
│   │   ├── core/                # 配置、安全、中间件、数据库、持久化
│   │   ├── engine/
│   │   │   ├── narrative/       # 阶段状态机 (conductor)
│   │   │   ├── empathy/         # 情感分析、节奏控制
│   │   │   ├── inference/       # 贝叶斯引擎、语义指纹、防御检测、校验器
│   │   │   └── chat_pipeline.py # 8 步骤全链路对话编排 (含 RAG 检索)
│   │   ├── llm/
│   │   │   ├── providers/       # 5 家 LLM 厂商 Provider
│   │   │   ├── prompts/         # 提示词模板管理
│   │   │   ├── embedder.py      # bge-large-zh 嵌入引擎
│   │   │   └── output_parser.py # LLM 结构化输出解析器
│   │   ├── models/              # SQLAlchemy 模型 (7 张表含 psychology_patterns)
│   │   ├── schemas/             # Pydantic Schema
│   │   └── services/            # 业务逻辑层 (含 PatternService + PatternRetriever)
│   ├── seed_data/
│   │   └── patterns.json        # 50 条心理学模式种子数据
│   ├── scripts/                 # 种子脚本、构建脚本
│   ├── run.py                   # 桌面启动器 (pywebview)
│   ├── persona_weaver.spec      # PyInstaller 打包配置
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/            # ChatBubble、ChatInput、PhaseIndicator
│   │   │   ├── report/          # PersonalityCard、CognitiveMap、WordCloud、TherapistNote
│   │   │   └── settings/        # ProviderSelector、ApiKeyInput、ConnectionTest
│   │   ├── hooks/               # useWebSocket
│   │   ├── lib/                 # API 客户端、WebSocket 客户端
│   │   ├── pages/               # Home、Chat、Report、Settings、Privacy、Terms
│   │   └── stores/              # Zustand 状态 (chatStore, configStore)
│   └── package.json
└── README.md
```

---

## RAG 心理学知识库

Persona Weaver 内建了一个基于向量检索的心理学模式库：

| 属性 | 值 |
|:---|:---|
| 模式数量 | 50 条（可扩展至 5000+） |
| 类别 | 防御机制、认知偏差、情感模式、人际关系、人格特质、应对策略 |
| 嵌入模型 | bge-large-zh-v1.5 (1024 维) |
| 检索方式 | 余弦相似度 + 阶段/防御标签加权 |
| 检索延迟 | < 50ms |

在对话 Pipeline 中，每轮用户输入都会被临时向量化，与模式库进行相似度检索，匹配到的心理学模式作为 `[检索参考]` 注入 LLM 系统提示词，提升分析的专业性和解释力。用户语料不入库、不持久化。

---

## 免责声明

本工具提供的报告仅为心理类型倾向参考，**不能替代专业心理诊断或治疗**。用户需年满 16 周岁。对话数据默认存储在本地 `~/.persona-weaver/` 目录，用户可随时在设置中清除。

---

## License

[MIT](LICENSE)
