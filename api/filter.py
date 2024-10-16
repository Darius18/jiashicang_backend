from flask import jsonify, make_response, Blueprint, request
import sqlite3

# 定义一个 Blueprint
filter_bp = Blueprint('filter', __name__)

def get_db_connection():
    """Connects to the SQLite database."""
    connection = sqlite3.connect('medical_users.db')
    connection.row_factory = sqlite3.Row  # This allows us to access columns by name
    return connection

@filter_bp.route('/api/filter', methods=['POST'])
def filter_users():
    # 获取前端传来的 JSON 数据
    filter_data = request.json
    
    # 构建查询语句的过滤条件
    filters = []
    params = []
    
    # 动态构建查询条件
    for key, value in filter_data.items():
        if value not in [None, ""]:  # 跳过空字符串和 None
            filters.append(f"{key} = ?")
            params.append(value)
    
    # 生成 WHERE 条件
    where_clause = " AND ".join(filters) if filters else "1=1"
    
    # 需要统计的字段
    fields_to_group_by = {
        "BMI类型": "BMI类型",
        "吸烟量": "吸烟量",
        "是否吸烟": "是否吸烟",
        "性别": "性别",
        "是否居家": "是否居家",
        "是否锻炼": "是否锻炼",
        "是否饮酒": "是否饮酒",
        "饮酒频率": "饮酒频率",
        "健康分类": "健康分类"
    }

    connection = get_db_connection()
    cursor = connection.cursor()

    # 统计总条数
    total_query = f"SELECT COUNT(*) as total_num FROM users WHERE {where_clause}"
    cursor.execute(total_query, params)
    total_num = cursor.fetchone()['total_num']

    # 初始化统计结果
    stats = {}
    
    # 遍历需要统计的字段，分别执行 GROUP BY 查询
    for stat_name, field in fields_to_group_by.items():
        query = f"SELECT {field}, COUNT(*) as count FROM users WHERE {where_clause} GROUP BY {field}"
        cursor.execute(query, params)
        results = cursor.fetchall()
        stats[stat_name] = {row[field] if row[field] else "空值": row['count'] for row in results}

    connection.close()

    # 构建返回的 JSON 响应
    response_data = {
        "total_num": total_num,
    }

    # 动态添加统计结果
    response_data.update(stats)

    return make_response(jsonify(response_data), 200)