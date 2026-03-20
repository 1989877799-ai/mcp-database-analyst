import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    # 连接到 SQLite 数据库（如果不存在则会自动创建）
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    print("正在创建数据库表...")
    
    # 1. 创建商品表 (products)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')

    # 2. 创建订单表 (orders)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        order_date DATE NOT NULL,
        status TEXT NOT NULL
    )
    ''')

    # 3. 创建订单明细表 (order_items)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    print("正在注入模拟数据...")

    # 插入商品数据
    products_data = [
        ('MacBook Pro M3', '电子产品', 12999.00),
        ('iPhone 15 Pro', '电子产品', 7999.00),
        ('Sony 降噪耳机', '电子产品', 1999.00),
        ('人体工学办公椅', '家居', 899.00),
        ('纯棉四件套', '家居', 299.00),
        ('手冲咖啡套装', '食品饮料', 350.00),
        ('全麦面包', '食品饮料', 25.00)
    ]
    cursor.executemany('INSERT INTO products (name, category, price) VALUES (?, ?, ?)', products_data)

    # 插入订单与订单明细数据 (重点模拟 2023年10月 的数据)
    statuses = ['已完成', '已发货', '处理中']
    
    # 获取刚刚插入的商品信息以便生成明细
    cursor.execute('SELECT id, price FROM products')
    product_pool = cursor.fetchall()

    for i in range(1, 51): # 生成 50 个模拟订单
        # 将日期集中在 2023年10月，部分在11月
        day_offset = random.randint(1, 40)
        order_date = (datetime(2023, 10, 1) + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        status = random.choice(statuses)
        customer_id = random.randint(1001, 1020)
        
        cursor.execute('INSERT INTO orders (customer_id, order_date, status) VALUES (?, ?, ?)', 
                       (customer_id, order_date, status))
        order_id = cursor.lastrowid
        
        # 为每个订单生成 1-3 个商品明细
        num_items = random.randint(1, 3)
        for _ in range(num_items):
            prod = random.choice(product_pool)
            product_id = prod[0]
            unit_price = prod[1]
            quantity = random.randint(1, 5)
            
            cursor.execute('''
            INSERT INTO order_items (order_id, product_id, quantity, unit_price) 
            VALUES (?, ?, ?, ?)
            ''', (order_id, product_id, quantity, unit_price))

    # 提交事务并关闭连接
    conn.commit()
    conn.close()
    print("✅ 数据库 'ecommerce.db' 初始化成功！测试数据已就绪。")

if __name__ == '__main__':
    create_database()