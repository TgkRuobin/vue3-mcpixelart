import mysql.connector
from mysql.connector import Error

import os

db_conf = {
  "host": os.getenv('DB_HOST'),
  "database": os.getenv('DB_NAME'),
  "user": os.getenv('DB_USER'),
  "password": os.getenv('DB_PASSWORD')
}

def query(sql, args):
  '''执行查询，返回结果'''
  try:
    connection = mysql.connector.connect(**db_conf)
    if connection.is_connected():
      cursor = connection.cursor(dictionary=True)
      cursor.execute(sql, args)
      result = cursor.fetchall()
      return {'result': result, 'ok': True}
  except Error as e:
    return {'ok': False, 'reason': e}
  finally:
    if connection.is_connected():
      cursor.close()
      connection.close()
        
def exec(sql, args):
  '''执行操作，不返回结果'''
  try:
    connection = mysql.connector.connect(**db_conf)
    if connection.is_connected():
      cursor = connection.cursor()
      cursor.execute(sql, args)
      connection.commit()
      return {'ok': True}
  except Error as e:
    return {'ok': False, 'reason': e}
  finally:
    if connection.is_connected():
      cursor.close()
      connection.close()
