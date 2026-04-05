from utils.net import new_art
from flask import Blueprint, request, jsonify
from litemapy import Region, BlockState

import pickle
import time
import uuid
import gzip
import os

enhance_bp = Blueprint('enhance', __name__, url_prefix='/')

STATIC_FOLDER = os.getenv('STATIC_FOLDER')
ENHANCE_MAX_LEN = os.getenv('ENHANCE_MAX_LEN')
    
def get_unique_filename():
    extension = '.litematic'
    timestamp = str(int(time.time() * 1000))  # 获取当前时间戳（毫秒级）  
    unique_filename = f"{timestamp}{uuid.uuid4()}{extension}"
    return unique_filename

@enhance_bp.route('/pixelartEnhance', methods=['POST'])
def scu_post():
  try:
    data = request.get_json()
    if 'size' in data and 'pipe' in data:
      l = data['size']['length']
      w = data['size']['width']
      h = data['size']['height']
      reg = Region(0,0,0,w,h,l)
      pipe = data['pipe']
      if len(pipe) > ENHANCE_MAX_LEN:
        return jsonify({'error': f'尺寸太大了!!无效请求'}), 400
      for item in pipe:
        reg[tuple(item[0])] = BlockState(item[1])
      schem = reg.as_schematic(name="Unnamed art", author="mcpixelart.com", description="Create your art of mc online.")
      fname = get_unique_filename()
      schem.save(os.path.join(STATIC_FOLDER, 'enhance', fname))

      x_ident = request.headers.get('X-IDENT')
      if not x_ident:
          x_ident = ''
      new_art('enhance', fname,x_ident)
      #备份
      with gzip.open(os.path.join(STATIC_FOLDER, 'enhance_backup', fname), 'wb') as f:
        pickle.dump(data, f)
      return jsonify({'url': fname}), 200
    else:
      return jsonify({'error': f'无效请求'}), 400
  except Exception as e:
    print('[error] enhance >', str(e))
    return jsonify({'error': '生成失败'}), 400
