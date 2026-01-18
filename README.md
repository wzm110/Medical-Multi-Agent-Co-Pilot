# 医学智能体系统 (Medical Agent System)

一个基于 LangGraph 的医学智能体系统，集成了前端UI、后端服务和医学知识库，能够根据用户的症状描述进行初步诊断、科室分诊并提供专业建议。

## 项目架构

本项目采用三层架构设计：

- **前端 UI** (`agent-chat-ui/`): 基于 Next.js 的聊天界面，用于与医学智能体进行交互
- **后端服务** (`app/`): 基于 LangGraph 和 FastAPI 的智能体服务，包含多个专科智能体和工作流
- **数据层** (`data/`): 医学知识库，包含预处理后的医学教材数据，用于 GraphRAG 系统

## 主要功能

- **症状采集**: 与用户交互，收集详细的症状信息
- **智能分诊**: 根据症状判断应就诊的科室
- **专科诊断**: 各专科智能体提供专业的诊断建议
- **决策融合**: 整合多科室智能体的建议，提供综合诊断
- **知识推理**: 基于 Graph RAG 的医学知识图谱支持

## 安装与准备

### 前置要求

- Python 3.10+
- Node.js 18+
- pnpm 或 npm
- Graph RAG 已构建完毕并启动在 8000 端口

### 环境变量配置

#### 后端环境变量 (app/.env)

```env
# 语言模型配置
MODEL_NAME=qwen3-max  # 模型名称
MODEL_PROVIDER=openai  # 模型提供商
OPENAI_API_KEY=your-api-key  # API密钥
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1  # API基础地址

# LangSmith 配置（用于追踪和调试）
LANGSMITH_PROJECT=new-agent

# Graph RAG API 配置
GRAPH_RAG_ENDPOINT=http://localhost:8000/query
GRAPH_RAG_API_KEY=your-api-key
```

#### 前端环境变量 (agent-chat-ui/.env)

```env
NEXT_PUBLIC_API_URL=http://localhost:8123  # 后端服务地址
NEXT_PUBLIC_ASSISTANT_ID=agent  # 智能体ID
```

## 启动步骤

### 1. 启动 Graph RAG 服务（前提条件）

确保 Graph RAG 已构建完毕并启动在 8000 端口。

### 2. 启动后端服务

```bash
# 方式一：使用 Uvicorn 直接启动
python -m uvicorn app.graphrag_fastapi:app --host 0.0.0.0 --port 8000 --reload

# 方式二：使用 LangGraph CLI（推荐）
cd app
langgraph serve
```

### 3. 启动 LangGraph Dev Server

```bash
langgraph dev --allow-blocking
```

### 4. 启动前端 UI

```bash
cd agent-chat-ui
pnpm install  # 首次启动需安装依赖
pnpm dev
```

## 服务访问地址

- 后端 API: http://localhost:8000 或 http://localhost:8123
- LangGraph UI: http://localhost:8123/ui
- 前端聊天界面: http://localhost:3000

## 项目结构

```
LangGraph/
├── agent-chat-ui/          # 前端聊天界面
│   ├── src/               # 前端源代码
│   ├── public/            # 静态资源
│   ├── package.json       # 前端依赖
│   └── README.md          # 前端文档
├── app/                   # 后端服务
│   ├── src/               # 后端源代码
│   │   └── agent/         # 智能体实现
│   │       ├── agents/    # 各专科智能体
│   │       ├── graph/     # 工作流图定义
│   │       └── tools/     # 工具函数
│   ├── tests/             # 测试文件
│   ├── pyproject.toml     # 项目配置
│   └── README.md          # 后端文档
├── data/                  # 医学数据
│   ├── 临床药物治疗学/     # 原始医学教材
│   ├── 数据/              # 预处理后的数据
│   ├── data_preprocessor_v2.py  # 数据预处理脚本
│   └── README.md          # 数据文档
└── README.md              # 项目总文档
```

## 核心组件说明

### 后端智能体

- **症状采集智能体**: 负责与用户交互，收集症状信息
- **分诊调度智能体**: 根据症状判断就诊科室
- **专科智能体**: 包括心血管内科、呼吸内科、消化内科等
- **决策融合智能体**: 整合各专科智能体的建议
- **Graph RAG 系统**: 提供医学知识支持

### 数据层

- 包含多本医学教材的 LaTeX 源文件
- 预处理为结构化的 CSV 数据块
- 按科室分类，支持 Graph RAG 查询
- 总数据块数: 9,817，覆盖 12 个科室

### 前端界面

- 基于 Next.js 构建的聊天界面
- 支持与 LangGraph 服务器的实时交互
- 可配置后端服务地址和智能体 ID

## 测试

### 后端测试

```bash
cd app
# 单元测试
python -m pytest tests/unit_tests/ -v

# 集成测试
python -m pytest tests/integration_tests/ -v

# Graph RAG 测试
python test_graph_rag.py
```

### 数据测试

```bash
cd data
# 数据分析
python analyze_data.py

# 分诊推荐演示
python triage_recommendation_demo.py
```

## 开发说明

### 代码规范

- 后端使用 ruff 和 mypy 进行代码质量控制
- 前端使用 ESLint 和 Prettier 进行代码格式化

### 添加新智能体

1. 在 `app/src/agent/agents/` 目录下创建新的智能体文件
2. 实现智能体的核心功能和节点
3. 在工作流中注册新智能体
4. 编写相应的测试用例

### 数据更新

1. 将新的医学教材添加到 `data/` 目录
2. 使用 `data_preprocessor_v2.py` 进行预处理
3. 按科室分离数据，更新 Graph RAG 知识库

## 注意事项

1. **医疗建议仅供参考**: 本系统提供的诊断和建议仅作为初步参考，不能替代专业医生的诊断
2. **紧急情况处理**: 如遇紧急医疗情况，请立即拨打当地急救电话或前往医院就诊
3. **数据隐私保护**: 请勿在测试环境中输入真实的个人敏感信息
4. **API 调用限制**: 请注意您使用的语言模型 API 的调用限制和费用

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过项目地址反馈：[项目GitHub链接]
