from utils.db import query, exec
import time
import uuid

def get_uid_from_uuid(uuid):
  '''根据uid获取uuid'''
  bk = query('SELECT * FROM user WHERE uuid=%s',(uuid,))
  if bk['ok'] and len(bk['result']) > 0:
    return {'ok': True, 'result': bk['result'][0]['uid']}
  else:
    return {'ok': False}

def get_ip(req):
  '''获取用户真实ip'''
  xff = req.headers.get('X-Forwarded-For', '').split(',')
  client_ip = ''
  if xff:
    client_ip = xff[0].strip()
  else:
    client_ip = req.headers.get('X-Real-IP', '')
  if not client_ip:
    client_ip = req.remote_add
  return client_ip

def new_art(type,name,uuid):
  '''数据库添加新作品'''
  bk = get_uid_from_uuid(uuid)
  if bk['ok']:
    uid = bk['result']
    exec(
      'insert into art (atype,afname,auuid,auid) values (%s,%s,%s,%s)', 
      (type,name,uuid,uid)
    )
    return True
  else:
    return False

def get_unique_filename():
  '''获取一个唯一文件名'''
  extension = '.litematic'
  timestamp = str(int(time.time() * 1000))  # 获取当前时间戳（毫秒级）  
  unique_filename = f"{timestamp}{uuid.uuid4()}{extension}"
  return unique_filename
