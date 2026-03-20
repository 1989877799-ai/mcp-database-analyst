"""
基于 FastMCP 的电商 SQLite MCP 服务。

将当前目录下的 ecommerce.db 暴露给大语言模型，通过 MCP Tools 进行只读查询与业务分析。
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# 路径与 MCP 实例
# ---------------------------------------------------------------------------

# 数据库文件与 server.py 位于同一目录，避免工作目录变化导致找不到文件
_DB_PATH = Path(__file__).resolve().parent / "ecommerce.db"

# FastMCP 服务名称，会出现在 MCP 客户端配置中，便于识别
mcp = FastMCP("ecommerce-sqlite")


def _get_connection() -> sqlite3.Connection:
    """创建指向本地 SQLite 的连接（行工厂便于按列名取字段）。"""
    if not _DB_PATH.is_file():
        raise FileNotFoundError(f"数据库文件不存在: {_DB_PATH}")
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# 只读 SQL 校验（简单字符串规则，拦截明显写操作）
# ---------------------------------------------------------------------------

# 禁止出现的 SQL 关键字（整词匹配，忽略大小写），防止 DROP/UPDATE 等修改数据或结构
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(?:DROP|UPDATE|INSERT|DELETE|ALTER|TRUNCATE|CREATE|REPLACE|ATTACH|DETACH)\b",
    re.IGNORECASE,
)

# 允许的查询必须以 WITH（公用表表达式）或 SELECT 开头
_ALLOWED_START = re.compile(r"^\s*(?:WITH|SELECT)\b", re.IGNORECASE)


def _validate_read_only_sql(sql_query: str) -> str | None:
    """
    校验 sql_query 是否可视为只读 SELECT。

    返回 None 表示通过；否则返回给模型看的错误说明字符串。
    """
    if not sql_query or not sql_query.strip():
        return "错误：sql_query 不能为空。"

    text = sql_query.strip()

    # 简单防多语句：不允许分号分隔出多条非空语句（避免第二条为写操作）
    segments = [s.strip() for s in text.split(";") if s.strip()]
    if len(segments) != 1:
        return "错误：仅允许单条 SELECT 查询，请勿使用多条语句或多余的分号。"

    single = segments[0]

    if _FORBIDDEN_KEYWORDS.search(single):
        return (
            "错误：检测到可能修改数据或结构的语句。"
            "本工具仅允许只读查询，请勿使用 DROP、UPDATE、INSERT、DELETE、ALTER 等关键字。"
        )

    if not _ALLOWED_START.match(single):
        return "错误：查询必须以 SELECT 或 WITH ... SELECT 形式开头。"

    return None


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_database_schema() -> str:
    """
    获取 ecommerce 库中三张核心表的 DDL（CREATE TABLE）及中文说明。

    无参数。供大语言模型在编写 SQL 前了解表名、字段类型与关联关系。
    """
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT name, sql
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
              AND name IN ('products', 'orders', 'order_items')
            ORDER BY
              CASE name
                WHEN 'products' THEN 1
                WHEN 'orders' THEN 2
                WHEN 'order_items' THEN 3
              END
            """
        )
        rows = cur.fetchall()

    ddl_blocks: list[str] = []
    for row in rows:
        name = row["name"]
        sql_ddl = row["sql"] or ""
        ddl_blocks.append(f"-- 表: {name}\n{sql_ddl}")

    overview = """
【表说明摘要】
- products: 商品主数据。id 为主键；name/category/price 描述商品。
- orders: 订单头。id 为主键；customer_id 客户；order_date 下单日期；status 状态。
- order_items: 订单行。order_id 关联 orders.id；product_id 关联 products.id；
  quantity 为数量；unit_price 为行上单价（可能与 products.price 不同，以行上为准）。

【关联】
- order_items.order_id -> orders.id
- order_items.product_id -> products.id
"""
    return "\n\n".join(ddl_blocks) + "\n" + overview


@mcp.tool()
def execute_read_only_sql(sql_query: str) -> str:
    """
    执行只读 SQL，将结果集以 JSON 字符串返回。

    参数 sql_query: 单条 SELECT（或 WITH ... SELECT）。会先进行关键字校验，拒绝写操作。
    """
    err = _validate_read_only_sql(sql_query)
    if err:
        return json.dumps({"ok": False, "error": err}, ensure_ascii=False)

    segments = [s.strip() for s in sql_query.strip().split(";") if s.strip()]
    single = segments[0]

    try:
        with _get_connection() as conn:
            cur = conn.cursor()
            cur.execute(single)
            cols = [d[0] for d in cur.description] if cur.description else []
            raw_rows = cur.fetchall()
            # sqlite3.Row 转为普通 dict，便于 JSON 序列化
            data = [dict(zip(cols, [row[c] for c in cols])) for row in raw_rows]
    except sqlite3.Error as e:
        return json.dumps(
            {"ok": False, "error": f"SQL 执行失败: {e}"},
            ensure_ascii=False,
        )

    payload: dict[str, Any] = {
        "ok": True,
        "columns": cols,
        "row_count": len(data),
        "rows": data,
    }
    return json.dumps(payload, ensure_ascii=False, default=str)


@mcp.tool()
def get_top_selling_products(limit: int = 3, start_date: str = "2023-10-01") -> list[dict[str, Any]]:
    """
    业务封装：统计 start_date（含）之后销量最高的商品。

    参数:
    - limit: 返回前 N 名，默认 3。
    - start_date: 起始日期，格式 YYYY-MM-DD，默认 2023-10-01。

    内部联查 orders、order_items、products：
    - 总销量 = SUM(quantity)
    - 总销售额 = SUM(quantity * unit_price)

    返回字典列表，字段含 product_id、name、category、total_quantity、total_revenue。
    """
    if limit < 1:
        limit = 1

    sql = """
    SELECT
        p.id AS product_id,
        p.name AS name,
        p.category AS category,
        SUM(oi.quantity) AS total_quantity,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM orders AS o
    INNER JOIN order_items AS oi ON o.id = oi.order_id
    INNER JOIN products AS p ON oi.product_id = p.id
    WHERE o.order_date >= ?
    GROUP BY p.id, p.name, p.category
    ORDER BY total_quantity DESC
    LIMIT ?
    """

    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, (start_date, limit))
        rows = cur.fetchall()

    return [
        {
            "product_id": r["product_id"],
            "name": r["name"],
            "category": r["category"],
            "total_quantity": int(r["total_quantity"]),
            "total_revenue": float(r["total_revenue"]),
        }
        for r in rows
    ]


if __name__ == "__main__":
    # 通过标准输入输出与 MCP 宿主（如 Cursor、Claude Desktop）通信
    mcp.run(transport="stdio")
