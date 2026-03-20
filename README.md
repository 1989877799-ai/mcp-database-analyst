# MCP Local Database Analyst 🤖📊

这是一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的自定义 Server。它允许大语言模型（如 Claude Desktop / Cursor）直接连接并分析本地 SQLite 数据库，实现自然语言到业务报表的无缝转换。

## 核心功能
- 📂 **Schema 提取**：自动向 LLM 暴露数据库表结构。
- 🛡️ **安全沙箱查询**：支持执行只读（SELECT）SQL 分析数据，拦截破坏性语句。
- 📈 **业务逻辑封装**：内置特定业务分析工具（如畅销品分析）。

## 快速启动
1. 安装依赖：`pip install mcp`
2. 初始化测试数据：`python init_db.py` (会自动生成 `ecommerce.db`)
3. 运行服务：按需将其配置到 Cursor 或 Claude Desktop 中。
   - Command: `python /绝对路径/server.py`