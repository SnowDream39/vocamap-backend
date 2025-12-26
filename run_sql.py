import psycopg2

# 数据库连接配置
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "little_project",
    "user": "postgres",
    "password": "11111111",
}

def execute_sql_file(file_path):
    # 读取 SQL 文件
    with open(file_path, "r", encoding="utf-8") as f:
        sql_commands = f.read()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 直接执行所有 SQL
        cur.execute(sql_commands)

        conn.commit()
        cur.close()
        conn.close()

        print("SQL 文件执行成功！")

    except Exception as e:
        print("执行 SQL 时发生错误：", e)

if __name__ == "__main__":
    execute_sql_file("alter_column.sql")
