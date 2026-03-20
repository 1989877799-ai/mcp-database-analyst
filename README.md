
-----

````markdown
# 📊 MCP Database Analyst Server

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue)
![MCP Protocol](https://img.shields.io/badge/Protocol-MCP-green)
![License](https://img.shields.io/badge/License-MIT-orange)

基于 **Model Context Protocol (MCP)** 标准构建的本地数据库分析 AI Agent 服务。

本项目旨在打破大语言模型（LLM）与本地结构化数据之间的壁垒。通过将数据库查询能力封装为标准 MCP Tools，使得 Cursor、Claude Desktop 等现代 AI 客户端能够以自然语言交互的方式，安全、自主地读取本地 SQLite 数据库，并直接生成具有商业洞察价值的 Markdown 数据报表。

## ✨ 核心特性 (Core Features)

- **🤖 零代码数据分析 (NL2SQL)**：无需手写 SQL，使用自然语言向 AI 提问即可拉取并分析数据。
- **🛡️ 安全沙箱查询 (Security Sandbox)**：内置 SQL 拦截器，强制校验 AST 或关键字，严格拒绝 `DROP`、`UPDATE`、`DELETE` 等破坏性 DML/DDL 语句，仅允许只读（SELECT）操作。
- **📈 业务语义对齐 (Business Aligned)**：不仅返回 Raw JSON 数据，更能通过 LLM 的推理能力，自动将生硬的结构化数据转化为包含“核心摘要”、“明星榜单”和“滞销预警”的结构化商业报表。
- **🔌 无缝集成 (Seamless Integration)**：完美兼容支持 MCP 协议的顶级 AI 效率工具（Claude Desktop, Cursor 等）。

## 🏗️ 架构概览 (Architecture)

```mermaid
graph LR
    User[👤 用户 (自然语言提问)] --> Client[🖥️ MCP Client (Cursor/Claude)]
    Client -- MCP Protocol --> Server[⚙️ Python MCP Server]
    Server -- 1. get_database_schema --> DB[(📦 本地 SQLite)]
    Server -- 2. execute_read_only_sql --> DB
    DB -. 返回结果集 (JSON) .-> Server
    Server -. 传递 Context .-> Client
    Client -. LLM 渲染报表 .-> User
````

## 🚀 快速开始 (Quick Start)

### 1\. 环境准备

确保你的本地环境已安装 Python 3.10 或更高版本。

```bash
# 克隆仓库
git clone [https://github.com/你的用户名/mcp-database-analyst.git](https://github.com/你的用户名/mcp-database-analyst.git)
cd mcp-database-analyst

# 安装 MCP 官方 SDK 及相关依赖
pip install mcp
```

### 2\. 初始化测试数据

为了方便测试，本项目内置了电商场景的模拟数据生成器。运行以下命令即可在本地生成包含千万级（模拟）营收数据的 `ecommerce.db` 数据库文件：

```bash
python init_db.py
```

> **注**：`ecommerce.db` 已加入 `.gitignore`，不会被提交到远程仓库以保障数据安全。

### 3\. 接入 MCP Client (以 Cursor 为例)

1.  打开 Cursor 设置面板 (`Cmd/Ctrl + ,`)
2.  导航至 **Features** -\> **MCP**
3.  点击 **+ Add New MCP Server**
4.  填写配置：
      - **Name**: `Local-DB-Analyst`
      - **Type**: `command`
      - **Command**: `python /你的绝对路径/mcp-database-analyst/server.py`
5.  保存并确认指示灯变绿。

## 💡 最佳实践 (Prompt Engineering)

配置完成后，你可以直接在 Cursor Chat 或 Claude 中发送以下 Prompt 体验“魔法”：

**场景一：结构化商业报表生成**

> "调用你的数据库工具，分析一下上个月（2023年10月）销量最高的三个产品，以及表现最差的商品类别。请严格按照 Markdown 格式输出业务报表，包含：1. 核心摘要；2. 明星产品榜单（表格）；3. 滞销预警；4. 业务建议。"

**场景二：开放式数据探索**

> "帮我查一下，目前有哪些顾客的订单还在‘处理中’？针对这些未完成的订单，我们大概还有多少潜在营收卡在流程里？请用专业的数据简报形式呈现给我。"

## 📁 项目结构 (Project Structure)

```text
mcp-database-analyst/
├── init_db.py          # 模拟电商数据库生成脚本
├── server.py           # MCP Server 核心逻辑与 Tools 注册
├── .gitignore          # Git 忽略配置（保护本地数据）
└── README.md           # 项目文档
```

## 🛣️ 未来路线图 (Roadmap)

  - [x] 基于 SQLite 的基础查询与架构提取
  - [x] DML 操作拦截与安全防护
  - [ ] 支持 PostgreSQL / MySQL 生产级数据库接入
  - [ ] 集成 Mermaid.js 语法生成可视化数据图表
  - [ ] Docker 容器化部署支持

## 📄 许可证 (License)

本项目基于 [MIT License](https://www.google.com/search?q=LICENSE) 开源，欢迎自由 Fork 与二次开发。

```



