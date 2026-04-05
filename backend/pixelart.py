from utils.net import new_art, get_unique_filename
from flask import Blueprint, request, jsonify
from litemapy import Region, BlockState

import pickle
import gzip
import os
import re

pixelart_bp = Blueprint('/', __name__)

STATIC_FOLDER = os.getenv('STATIC_FOLDER')
PIXEL_MAX_LEN = os.getenv('PIXEL_MAX_LEN')

def rotate90(matrix):  
    return [list(reversed(row)) for row in zip(*matrix)]
def rotate180(matrix):  
    return [list(reversed(row)) for row in matrix[::-1]]
def rotate270(matrix):  
    return list(reversed([list(row)[::-1] for row in zip(*reversed(matrix))]))

def create2dlite(data,dir,rot):
    '''生成像素画'''
    #旋转
    if rot == 90:
        data = rotate90(data)
    elif rot == 180:
        data = rotate180(data)
    elif rot == 270:
        data = rotate270(data)

    h = len(data)
    w = len(data[0])
    if dir == 'z':
        reg = Region(0,0,0,w,1,h)
        for y in range(h):
            for x in range(w):
                if data[y][x] == 'air': continue
                reg[x,0,y] = BlockState('minecraft:'+data[y][x])
    elif dir == 'y':
        reg = Region(0,0,0,1,h,w)
        for y in range(h):
            for x in range(w):
                if data[y][x] == 'air': continue
                reg[0,h-y-1,w-x-1] = BlockState('minecraft:'+data[y][x])
    else:
        reg = Region(0,0,0,w,h,1)
        for y in range(h):
            for x in range(w):
                if data[y][x] == 'air': continue
                reg[x,h-y-1,0] = BlockState('minecraft:'+data[y][x])
    # Region尺寸:东西方向 上下方向 南北方向
    # Region坐标增加的方向:西->东 下->上 北->南
    schem = reg.as_schematic(name="Unnamed Pixel Art", author="mcpixelart.com", description="Create your art of mc online.")
    fname = get_unique_filename()

    schem.save(os.path.join(STATIC_FOLDER, 'lite', fname))
    return fname

def check_matrix(variable):
    '''检查图像合法性'''
    # 首先检查变量是否是列表
    if not isinstance(variable, list):
        return False, "格式错误"

    # 检查列表中的每个元素是否也是列表（即二维矩阵）
    if not all(isinstance(row, list) for row in variable):
        return False, "图片无效"

    # 获取矩阵的行数和列数  
    num_rows = len(variable)
    if num_rows == 0:  # 空列表不是有效的矩阵
        return False, "空图像"

    num_cols = len(variable[0])  # 假设所有行都有相同的列数

    # 检查每一行的列数是否相同
    if not all(len(row) == num_cols for row in variable):
        return False, "图片无效"

    # 检查矩阵的每一维的大小是否在 1 到 PIXEL_MAX_LEN 之间
    if not (1 <= num_rows <= PIXEL_MAX_LEN and 1 <= num_cols <= PIXEL_MAX_LEN):
        return False, f"尺寸超出了{PIXEL_MAX_LEN}px"
    # print(f"Image size:{num_cols}*{num_rows}")
    return True, '图像正确'

def backup_img(fname,arr):
    '''以二维数组方式保存该图片'''
    fpath = os.path.join(STATIC_FOLDER, 'image_backup', fname)
    with gzip.open(fpath, 'wb') as f:
        pickle.dump(arr, f)
    return fpath

@pixelart_bp.route('/pixelart', methods=['POST'])
def pixel_post():
    try:
        data = request.get_json()
        #默认
        rot = 0
        dir = 'z'

        if 'dir' in data:
            dir = data['dir']
            if not dir in ['x','y','z']:
                return jsonify({'error': '无效朝向'}), 400
        if 'rot' in data:
            rot = data['rot']
            if not rot in [0,90,180,270]:
                return jsonify({'error': '无效角度'}), 400

        if 'art' in data:
            array = data['art']
            is_array_valid, check_msg = check_matrix(array)
            if(not is_array_valid):
                return jsonify({'error': check_msg}), 400

            name_cb = create2dlite(array,dir,rot)
            backup_img(name_cb, array)

            x_ident = request.headers.get('X-IDENT')
            if not x_ident:
                x_ident = ''
            new_art('art', name_cb,x_ident)

            return jsonify({'url': name_cb})
        else:
            return jsonify({'error': '无效请求'}), 400
    except Exception as e:
        print('[error] pixelart >', str(e))
        return jsonify({'error': f'请求失败'}), 400

def backup_scu(fname,arr):
    '''以数组方式保存该雕塑'''
    with gzip.open(os.path.join(STATIC_FOLDER, 'sculpture_backup', fname), 'wb') as f:
        pickle.dump(arr, f)

def check_3d(data):
    '''检查雕塑数据格式有效性'''
    MAX_VALUE = 500    # 单个维度最大值
    if not isinstance(data, list):
        return False, '非法数据'
    if len(data) == 0:
        return False, '空的雕塑'
    # 遍历列表中的每个元素  
    for element in data:  
        # 检查元素是否是包含三个元素的列表  
        if not (isinstance(element, list) and len(element) == 3):  
            return False, '非法数据'
          
        # 检查元素中的每个值是否是非负整数  
        for value in element:  
            if not isinstance(value, int) or value < 0 or value > MAX_VALUE:  
                return False, f'超出{MAX_VALUE}范围'
    # 如果所有检查都通过，则返回True  
    return True, 'ok'

def get3dsize(data):
    '''得到三维尺寸'''
    x_coords, y_coords, z_coords = zip(*data)   
    min_point = [min(x_coords), min(y_coords), min(z_coords)]  
    max_point = [max(x_coords), max(y_coords), max(z_coords)]
    dimensions = [int(max_coord - min_coord + 1) for max_coord, min_coord in zip(max_point, min_point)] 
    return dimensions

def create3dlite(data):
    size = get3dsize(data)
    reg = Region(0,0,0,size[0],size[1],size[2])
    # Region尺寸:东西方向 上下方向 南北方向
    # Region坐标增加的方向:西->东 下->上 北->南
    schem = reg.as_schematic(name="Unnamed Sculpture", author="mcpixelart.com", description="Create your art of mc online.")
    fname = get_unique_filename()
    stone = BlockState('minecraft:stone')
    for pos in data:
        reg[pos[0],pos[1],pos[2]] = stone
    schem.save(os.path.join('..','scu',fname))
    return fname

@pixelart_bp.route('/sculpture', methods=['POST'])
def scu_post():
    try:
        data = request.get_json()

        if 'scu' in data:
            array = data['scu']
            is_valid,desp = check_3d(array)
            if not is_valid:
                return jsonify({'error': desp}), 400

            name_cb = create3dlite(array)
            x_ident = request.headers.get('X-IDENT')
            if not x_ident:
                x_ident = ''

            backup_scu(name_cb,array)
            new_art('sculpture', name_cb,x_ident)
            return jsonify({'url': name_cb})
        else:
            return jsonify({'error': '无效请求'}), 400
    except Exception as e:
        print('[error] sculpture >', str(e))
        return jsonify({'error': f'请求失败'}), 400

@pixelart_bp.route('/reload', methods=['GET'])
def reload():
    try:
        fname = request.args.get('fname', '')
        #检查文件名合法性
        VALID_FILENAME_CHARS = re.compile(r'^[A-Za-z0-9-]+$')
        if not VALID_FILENAME_CHARS.match(fname):
            return jsonify({"error": "错误的链接"}), 400

        fpath = os.path.join(STATIC_FOLDER, 'image_backup/', fname + '.litematic')
        if os.path.exists(fpath):
            with gzip.open(fpath, 'rb') as f:
                arr_loaded = pickle.load(f)
            return jsonify({"image": arr_loaded}), 200
        else:
            return jsonify({"error": "链接不存在"}), 404
    except Exception as e:
        print('[error] reload >', str(e))
        return jsonify({'error': f'请求失败'}), 400
