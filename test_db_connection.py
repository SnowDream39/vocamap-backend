import asyncpg
import asyncio

async def test_connection():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="111111",
            database="little_project"
        )
        print("连接成功！🎉 PostgreSQL 连接正常！")

        # 测试简单查询
        result = await conn.fetch("SELECT version();")
        print("PostgreSQL 版本：", result[0]["version"])

        await conn.close()

    except Exception as e:
        print("连接失败❌")
        print(e)

asyncio.run(test_connection())