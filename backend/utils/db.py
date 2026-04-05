import os
from mysql.connector import pooling, Error
import logging

# ========================
# 基础配置
# ========================
db_conf = {
  "host": os.getenv("DB_HOST"),
  "database": os.getenv("DB_NAME"),
  "user": os.getenv("DB_USER"),
  "password": os.getenv("DB_PASSWORD"),
  "charset": "utf8mb4",
  "use_unicode": True,
  "autocommit": False
}

# ========================
# 日志
# ========================
logger = logging.getLogger("db")
logger.setLevel(logging.INFO)


# ========================
# 连接池
# ========================
try:
  pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=int(os.getenv("DB_POOL_SIZE", 10)),  # 根据gunicorn worker调整
    **db_conf
  )
except Exception as e:
  logger.exception("数据库连接池初始化失败")
  raise


# ========================
# 获取连接
# ========================
def get_conn():
  try:
    return pool.get_connection()
  except Error:
    logger.exception("获取数据库连接失败")
    raise


# ========================
# 查询函数
# ========================
def query(sql, args=None):
  connection = None
  cursor = None
  try:
    connection = get_conn()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(sql, args or ())
    result = cursor.fetchall()

    return {"ok": True, "result": result}

  except Error as e:
    logger.exception("数据库查询失败")
    return {"ok": False, "reason": "DATABASE_ERROR"}

  finally:
    if cursor:
      cursor.close()
    if connection:
      connection.close()  # 注意：这里是归还到连接池


# ========================
# 执行函数
# ========================
def exec(sql, args=None):
  connection = None
  cursor = None
  try:
    connection = get_conn()
    cursor = connection.cursor()

    cursor.execute(sql, args or ())
    connection.commit()

    return {"ok": True, "affected": cursor.rowcount}

  except Error:
    if connection:
      connection.rollback()

    logger.exception("数据库执行失败")
    return {"ok": False, "reason": "DATABASE_ERROR"}

  finally:
    if cursor:
      cursor.close()
    if connection:
      connection.close()


# ========================
# 事务支持
# ========================
class DBTransaction:
  def __enter__(self):
    self.conn = get_conn()
    self.cursor = self.conn.cursor(dictionary=True)
    return self.cursor

  def __exit__(self, exc_type, exc_val, exc_tb):
    if exc_type:
      self.conn.rollback()
    else:
      self.conn.commit()

    self.cursor.close()
    self.conn.close()
