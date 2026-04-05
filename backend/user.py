from utils.db import query, exec
from utils.net import get_ip, get_uid_from_uuid
from flask import Blueprint, request
import time
import uuid

user_bp = Blueprint('user', __name__, url_prefix='/user')

def generate_user_id():
  timestamp = int(time.time() * 1000)
  uuid_part = str(uuid.uuid4()).replace('-', '')
  user_id = f"{timestamp}{uuid_part}"
  return user_id

# 生成新用户
@user_bp.route('/genid', methods=['GET'])
def get_unique_user_id():
    try:
        userid = generate_user_id()
        uname = '用户' + userid[5:15]
        uip = get_ip(request)
        bk = exec('insert into user (uuid,uname,uip) values (%s,%s,%s)', (userid,uname,uip))
        if bk['ok']:
            return {'uuid': userid, 'uname': uname}, 200
        else:
            return {'error': '生成用户标识失败'}, 500
    except Exception as e:
        print('[error] genid >', str(e))
        return {'error': '生成用户标识失败'}, 500

# 改名
@user_bp.route('/cname', methods=['POST'])
def post_change_user_name():
    try:
        x_ident = request.headers.get('X-IDENT')
        data = request.get_json()
        if not 'name' in data: return {'error': '非法请求'}, 403
        uname = data['name'].strip()
        if (len(uname) == 0 or len(uname) >= 20): return {'error': '非法请求'}, 403
        if x_ident:
            bk = exec('update user set uname = %s where uuid = %s', (uname,x_ident))
            if bk['ok']:
                return {'uuid': x_ident, 'uname': uname}, 200
            else:
                return {'error': '更改失败'}, 401
        else:
            return {'error': '未登录用户'}, 401
    except Exception as e:
        print('[error] cname >', str(e))
        return {'error': '更改失败'}, 500

# 历史作品
@user_bp.route('/history', methods=['GET'])
def get_history():
    try:
        x_ident = request.headers.get('X-IDENT')
        cmd = f'SELECT adesc AS desciption,aid AS id,afname AS fname,aname AS name,atype AS type,ashare AS share,atime AS time,alike AS hot FROM art WHERE avisiable=1 AND auuid=%s'
        bk = query(cmd,(x_ident,))
        if bk['ok']:
            result = bk['result']
            return result, 200
        else:
            reason = bk['reason']
            return {'error': '读取数据库失败'}, 500
        
    except Exception as e:
        print('[error] history >', str(e))
        return {'error': '获取内容列表失败'}, 500

# 从uid获得uname
@user_bp.route('/uname', methods=['GET'])
def get_uname_from_uid():
    try:
        uid = request.args.get('uid', default=None)
        cmd = 'SELECT uname FROM user WHERE uid=%s'
        bk = query(cmd, (uid,))
        if bk['ok']:
            uname = bk['result']
            return uname, 200
        else:
            return {'error': '未找到'}, 400
    except Exception as e:
        print('[error] uname >', str(e))
        return {'error': '查询出错'}, 500
    
# 从uuid登录
@user_bp.route('/login', methods=['GET'])
def get_login():
    try:
        x_ident = request.headers.get('X-IDENT')
        cmd = 'SELECT uid,uname FROM user WHERE uuid=%s'
        bk = query(cmd, (x_ident,))
        if bk['ok']:
            userinfo = bk['result']
            return userinfo, 200
        else:
            return {'error': '未找到'}, 400
    except Exception as e:
        print('[error] login >', str(e))
        return {'error': '查询出错'}, 500
    
# 点赞
@user_bp.route('/like', methods=['POST'])
def post_plg_like():
    try:
        x_ident = request.headers.get('X-IDENT')
        if x_ident:
            gufu = get_uid_from_uuid(x_ident)
            if gufu['ok']:
                uid = gufu['result']
                data = request.get_json()
                if not 'id' in data: return {'error': '非法请求'}, 403
                bk1 = query('SELECT * FROM conduct WHERE coper=%s AND ctar=%s AND clike=1', (uid,data['id']))
                if bk1['ok']:
                    if len(bk1['result']) > 0:
                        return "您已经点过赞了", 200
                    else:
                        bk2 = exec('INSERT INTO conduct (coper,ctar,clike) VALUES (%s,%s,1)', (uid,data['id']))
                        if bk2['ok']:
                            return '点赞成功', 200
                        else:
                            return {'error': '点赞失败'}, 400
                else:
                    return {'error': '服务器查询失败'}, 400
            else:
                return {'error': '非法用户'}, 401
        else:
            return {'error': '未登录用户'}, 401
    except Exception as e:
        print('[error] like >', str(e))
        return {'error': '服务器出错了'}, 500

# 踩
@user_bp.route('/dislike', methods=['POST'])
def post_plg_dislike():
    try:
        x_ident = request.headers.get('X-IDENT')
        if x_ident:
            gufu = get_uid_from_uuid(x_ident)
            if gufu['ok']:
                uid = gufu['result']
                data = request.get_json()
                if not 'id' in data: return {'error': '非法请求'}, 403
                bk = exec('INSERT INTO conduct (coper,ctar,cdislike) VALUES (%s,%s,%s)', (uid,data['id'],1))
                if bk['ok']:
                    return '已点踩', 200
                else:
                    return {'error': '点踩失败'}, 400
            else:
                return {'error': '非法用户'}, 401
        else:
            return {'error': '未登录用户'}, 401
    except Exception as e:
        print('[error] dislike >', str(e))
        return {'error': '服务器出错了'}, 500

# 通过uid获取用户名
@user_bp.route('/unamelist', methods=['POST'])
def post_get_uname_list():
    try:
        x_ident = request.headers.get('X-IDENT')
        if x_ident:
            data = request.get_json()
            if len(data) > 12 * 30: return {'error': '非法请求'}, 403 # 一次最多查询的数目等于页面展示的最多作品数
            queryStatement = f"SELECT uid, uname FROM user WHERE uid IN ({','.join(['%s'] * len(data))})"
            bk = query(queryStatement, data)
            if bk['ok']:
                
                return bk['result'], 200
            else:
                return {'error': '查询用户名失败'}, 400
        else:
            return {'error': '未登录用户'}, 401
    except Exception as e:
        print('[error] unamelist >', str(e))
        return {'error': '服务器查询出错'}, 500
