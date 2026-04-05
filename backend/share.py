from utils.db import query, exec
from flask import Blueprint, request
import os

share_bp = Blueprint('share', __name__, url_prefix='/share')

FEED_MAX_LEN = os.getenv('FEED_MAX_LEN')

# feed
@share_bp.route('/feed', methods=['GET'])
def get_feed():
    try:
        filter = request.args.get('filter', default=None)
        sort = request.args.get('sort', default=None)
        allow_filter = ['all', 'art', 'enhance', 'sculpture', 'music']
        allow_sort = ['hot', 'new', 'random']
        if (not filter in allow_filter) or (not sort in allow_sort):
            return {'error': '错误的参数'}, 400

        statement_sort = ''
        if sort == 'new':
            statement_sort = 'ORDER BY atime DESC'
        elif sort == 'hot':
            statement_sort = 'ORDER BY alike DESC'
        else:
            statement_sort = 'ORDER BY RAND()'

        statement_filter = ''
        if filter == 'all':
            statement_filter = f'1=%s'
            filter = 1
        else:
            statement_filter = f'atype=%s'
        cmd = f'SELECT adesc AS desciption,aid AS id,afname AS fname,alike AS hot,aname AS name,atype AS type,atime AS time,auid AS uid FROM art WHERE avisiable=1 AND ashare=1 AND {statement_filter} {statement_sort} LIMIT %s'
        bk = query(cmd,(filter,FEED_MAX_LEN))
        if bk['ok']:
            result = bk['result']
            return result, 200
        else:
            reason = bk['reason']
            return {'error': '读取数据库失败'}, 500

    except Exception as e:
        print('[error] feed >', str(e))
        return {'error': '获取内容列表失败'}, 500

# 分享作品 / 取消分享作品
@share_bp.route('/share', methods=['POST'])
def post_share():
    try:
        x_ident = request.headers.get('X-IDENT')
        if x_ident:
            data = request.get_json()
            if 'fname' in data and 'name' in data and 'desc' in data:
                name = data['name']
                desc = data['desc']
                if len(name) >= 20 or len(desc) >= 100:
                    return {'error': '非法请求'}, 403
                fname = data['fname']
                cmd_query = 'SELECT * FROM art WHERE afname=%s AND auuid=%s'
                bk_query = query(cmd_query, (fname, x_ident))
                if bk_query['ok'] and len(bk_query['result']) > 0:
                    if 'share' in data and data['share'] == False:
                        cmd_share = 'UPDATE art SET ashare=%s WHERE afname=%s AND auuid=%s'
                        bk_share = exec(cmd_share, (0, fname, x_ident))
                    else:
                        cmd_share = 'UPDATE art SET ashare=%s,aname=%s,adesc=%s WHERE afname=%s AND auuid=%s'
                        bk_share = exec(cmd_share, (1, name, desc,fname, x_ident))
                    if bk_share['ok']:
                        return '分享成功', 200
                    else:
                        return {'error': '数据库操作失败;分享失败'}, 400
                else:
                    return {'error': '作品不存在/不是您制作的'}, 400
            else:
                return {'error': '非法请求'}, 403
        else:
            return {'error': '用户未登录'}, 401
    except Exception as e:
        print('[error] share >', str(e))
        return {'error': '分享失败'}, 500
