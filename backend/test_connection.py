# test_connection.py
import pymysql
from backend import config

try:
    conn = pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASS,
        database=config.MYSQL_DB,
        port=config.MYSQL_PORT
    )
    print("✅ Conexión exitosa a MySQL ->", config.MYSQL_DB)
    conn.close()
except Exception as e:
    print("❌ Error de conexión:", e)
