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

### 下载运行

从 [Releases](../../releases) 页面下载最新 `PersonaWeaver.exe`，双击运行即可。程序会自动打开桌面窗口。

### 配置 LLM

启动后在设置页面选择 LLM 厂商并填入 API Key，点击"测试连接"验证通过后即可开始对话。

> ⚠️ 建议使用一个全新的 API Key，避免在其他 AI 应用中的聊天记录被当作上下文影响对话质量。

### 从源码构建

```bash
# 1. 构建前端
cd frontend
pnpm install && pnpm build

# 2. 复制静态文件
Copy-Item -Recurse frontend/dist backend/static

# 3. 构建 .exe
cd backend
python -m PyInstaller --clean persona_weaver.spec
# 输出: backend/dist/PersonaWeaver.exe
```

前置依赖: Python 3.11-3.13, Node.js 20+, pnpm 9+

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
| 后端框架 | Python 3.13 + FastAPI |
| 数据库 | SQLite (aiosqlite) |
| 打包 | PyInstaller + pywebview |
| 前端 | React 18 + Vite + TypeScript |
| UI | TailwindCSS |
| 图表 | ECharts |
| 分词 | jieba |

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
│   └── build_exe.ps1         # Windows .exe 构建脚本
├── .github/                  # Issue/PR 模板
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

---

## 修复记录

### 2025-05-13 — 五大问题集中修复

#### 1. 顶部状态栏粘性固定
- **问题**: 设置、当前推断状态、轮次、对话阶段等信息随页面滚动被覆盖消失
- **修复**: `frontend/src/pages/Chat.tsx` — `<header>` 和 `<PhaseIndicator>` 包裹在 `sticky top-0 z-10` 容器中，滚动时始终固定在页面上方

#### 2. 模型输出截断 — "压缩回捞"
- **问题**: 对话后期模型输出内容被截断，影响阅读完整性
- **根因**: `chat_pipeline.py` 硬编码 `max_tokens=2048`，系统提示词要求输出 JSON 结构体，与 `doctor_reply` 共用 token 预算；JSON 截断后解析失败，fallback 再截至 500 字符
- **修复**:
  - 系统提示词 `doctor_reply` 增加 "控制在600字以内" 指引
  - 新增 `_compress_reply()` 函数：检测到 `finish_reason == "length"` 或内容 >2000 字符时，调轻量 LLM 压缩请求
  - `output_parser.py` fallback 截断 500 → 2000 字符

#### 3. 导出报告格式与提示
- **问题**: 导出报告后不知存储位置；HTML 格式不便于分享；exe 重启后报告丢失
- **修复**:
  - `frontend/src/pages/Report.tsx` — 使用 `html2canvas` + `jsPDF` 替代 HTML 导出，支持 PNG 图片和 A4 PDF，导出后 toast 提示
  - `chat_pipeline.py` — 报告生成时同步持久化到 SQLite 数据库

#### 4. 人格分析计算 — 多层锁死防御
- **问题**: 第一轮对话后人格类型不再变化；认知地图数据残缺
- **根因**: 多层级锁死——(a) `OBSERVATION_WEIGHT=3.0` 导致贝叶斯 5 轮内收敛；(b) 系统提示词反馈环：Bayesian 聚合值送回 LLM 引导"确认"；(c) LLM 上下文锚定偏差；(d) 提前退出阈值对慢热用户过早触发；(e) 维度间非正交污染
- **修复**:
  - `bayesian.py` — `OBSERVATION_WEIGHT` 3.0→1.0；新增 `DECAY_RATE=0.9` 时间衰减因子；新增 MBTI 历史追踪和 `mbti_stable_for()` 方法
  - `chat_pipeline.py` — 打破反馈环（不再用 Bayesian 聚合值覆盖 `state.dimensions`）；新增 "独立评估规则" 缓解 LLM 锚定偏差；收敛判据改为组合判据；新增 `_persist_dimension_snapshot` 每轮写维度快照；新增 `_validate_inference` 接入校验器
  - `conductor.py` — `CONFIDENCE_THRESHOLD` 0.85→0.70；提前跳出增加最小 10 轮保底
  - `defense.py` — 修复 `relevant_chars` 从未递增导致 `overall_invalid_rate` 恒为 1.0 的 bug
  - `report_generator.py` — 认知地图 HTML 从占位文字改为完整三维度条形图

#### 5. 首次设置 API Key 提醒
- **问题**: 未提醒用户使用全新 API Key，可能混入其他 AI 应用的历史对话上下文
- **修复**: `frontend/src/pages/Settings.tsx` — 欢迎横幅增加 "建议使用全新的 API Key" 安全提醒

### 2025-05-13 — 问题4深度修复 v4

#### A. 认知地图雷达图重写
- **问题**: 内向/直觉/感知型用户的雷达图几乎空白（`Math.max(0, score)` 将所有负值抹为0）；T_F 符号约定前后端相反（后端正=F情感，前端正=T思维）；轴标签仅标注单一极点
- **修复**: `frontend/src/components/report/CognitiveMap.tsx` — `toSeriesData()` 改用 `Math.abs()`；INDICATORS 改为双极标注（"内向 I ⟷ 外向 E"）；T_F 符号与后端对齐；每个场景显示 MBTI 偏好方向

#### B. 系统提示词去除数值锚定
- **问题**: 系统提示词中 `[当前维度] E_I=0.65...` 和 `[置信度] E_I=0.85...` 与"独立评估规则"形成矛盾——数值锚定效应强于文本指令，LLM 倾向于维持已有分数
- **修复**: `backend/app/engine/chat_pipeline.py` — 删除 L369-370 的维度和置信度数值行，替换为定性描述"不预设结论，不参考之前的评分数值"

#### C. 导出报告修复（webview 兼容）
- **问题**: `URL.createObjectURL` + `<a download>` 在 pywebview 嵌入式浏览器中不触发下载 UI，用户找不到文件
- **修复**: `frontend/src/pages/Report.tsx` — PDF 改用 `window.print()` 调起系统打印对话框；PNG 改用 `showSaveFilePicker()` 让用户选择保存位置，不支持时回退到传统下载

#### D. 认知地图数据修正
- **问题**: `build_cognitive_map()` 的 12 个场景乘数均为硬编码常量（work: E_I×1.1, crisis: J_P×-0.4...），与用户对话内容无关
- **修复**: `backend/app/services/report_generator.py` — 移除全部硬编码乘数，三个场景统一使用 Bayesian 原始分数

#### E. 推理调试接口
- **需求**: 从头完整对话测试耗时太长
- **实现**: `backend/app/api/routes/debug.py` — 新增 `POST /api/v1/debug/inference-test`，批量注入模拟消息运行管道，返回每轮 LLM 原始估计、Bayesian 聚合值、标准差、MBTI 变化历史和收敛状态
