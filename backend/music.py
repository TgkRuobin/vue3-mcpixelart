from utils.net import new_art, get_unique_filename
from flask import Blueprint, request, jsonify
from litemapy import Region, BlockState
import pickle
import gzip
import os
import math

import logging

logger = logging.getLogger('gunicorn.error')

music_bp = Blueprint('music', __name__, url_prefix='/')

STATIC_FOLDER = os.getenv('STATIC_FOLDER')

# 最大音轨数
MAX_TRACKS = os.getenv('MUSIC_MAX_TRACKS')
# 投影最长长度
MAX_LENGTH = os.getenv('MUSIC_MAX_LEN')

# 辅助方块
auxiliary = BlockState('minecraft:stone')
# 映射为音符盒下方方块
mapBlock = {
  "harp": BlockState("minecraft:air"),
  "snare": BlockState("minecraft:sand"),
  "bass": BlockState("minecraft:oak_planks"),
  "pling": BlockState("minecraft:glowstone"),
  "bell": BlockState("minecraft:gold_block"),
  "iron_xylophone": BlockState("minecraft:iron_block"),
  "basedrum": BlockState("minecraft:stone"),
  "bit": BlockState("minecraft:emerald_block"),
  "chime": BlockState("minecraft:packed_ice"),
  "flute": BlockState("minecraft:clay"),
  "guitar": BlockState("minecraft:white_wool"),
  "cow_bell": BlockState("minecraft:soul_sand"),
  "xylophone": BlockState("minecraft:bone_block", axis="y"),
  "didgeridoo": BlockState("minecraft:pumpkin"),
  "hat": BlockState("minecraft:glass"),
  "banjo": BlockState("minecraft:hay_block", axis="y"),
}
mapRepeater = {
  #三种中继器
  "re-n": BlockState(
    "minecraft:repeater",
    
      facing= "north",
      delay= "1",
      locked= "false",
      powered= "false"
    
  ),
  "re-s": BlockState(
    "minecraft:repeater",
    
      facing= "south",
      delay= "1",
      locked= "false",
      powered= "false"
    
  ),
  "re-w": BlockState(
    "minecraft:repeater",
    
      facing= "west",
      delay= "1",
      locked= "false",
      powered= "false"
    
  ),
}

def calculate_grid(n):
    """
    计算n个3x3方块的最小包围盒尺寸和每个方块的左下角坐标。

    参数：
    - n: int, 需要放置的3x3方块数量。

    返回：
    - width: int, 包围盒的宽度。
    - height: int, 包围盒的高度。
    - offsets: list of tuples, 每个3x3方块左下角的偏移量(offsetX, offsetY)。
    """
    if n <= 0:
        return 0, 0, []

    # 计算最小正方形网格的边长，以容纳n个3x3的方块，确保间距
    side_length = math.ceil(math.sqrt(n))

    # 每个方块实际占据4x4空间 (3x3方块 + 至少1单位间距)
    grid_size = side_length * 4

    # 初始化偏移量列表
    offsets = []

    # 放置方块
    for i in range(n):
        row = i // side_length
        col = i % side_length
        offset_x = col * 4  # 每列间隔4单位
        offset_y = row * 4  # 每行间隔4单位
        offsets.append((offset_x, offset_y))

    return grid_size, grid_size, offsets

def makeTrack(reg, data, offsetX, offsetY):
  '''
  根据给定的音轨数据data来填充reg

  需给定当前音轨的偏移量
  '''
  dlen = len(data['arr'])
  noteBlockName = data['name']
  noteBlock = mapBlock[noteBlockName]
  
  if dlen > 0:
    x = 0 # 不断增长
    y = 0 # +0、+2
    i = 0 # index
    direction = 'up' # S型前进

    for item in data['arr']:
      if item['play']:
        # 如果该瞬时有音则铺音符盒和对应发声方块
        reg[x, 2 + offsetY, y + offsetX] = BlockState('minecraft:note_block', 
          instrument = noteBlockName,
          note = str(item['pitch']),
          powered = 'false',
        )
        reg[x, 1 + offsetY, y + offsetX] = noteBlock
        # 发声方块下面需要垫辅助方块防止掉落
        reg[x, 0 + offsetY, y + offsetX] = auxiliary
      else:
        # 没有声直接铺辅助方块代替
        reg[x, 2 + offsetY, y + offsetX] = auxiliary

      # 最后一个音符盒后面不需要中继器
      if i == dlen - 1:
        continue

      # 根据前进方向铺中继器和辅助方块 并确定下一步的位置和前进方向
      if direction == 'up':
        reg[x, 2 + offsetY, 1 + offsetX] = mapRepeater['re-n']
        reg[x, 1 + offsetY, 1 + offsetX] = auxiliary

        y = 2
        direction = 'right1'
      elif direction == 'right1':
        reg[x + 1, 2 + offsetY, y + offsetX] = mapRepeater["re-w"]
        reg[x + 1, 1 + offsetY, y + offsetX] = auxiliary

        x += 2
        direction = 'down'
      elif direction == 'down':
        reg[x, 2 + offsetY, 1 + offsetX] = mapRepeater["re-s"]
        reg[x, 1 + offsetY, 1 + offsetX] = auxiliary

        y = 0
        direction = 'right2'
      else:
        reg[x + 1, 2 + offsetY, y + offsetX] = mapRepeater["re-w"]
        reg[x + 1, 1 + offsetY, y + offsetX] = auxiliary

        x += 2
        direction = 'up'
      i += 1

@music_bp.route('/musicGen', methods=['POST'])
def music_post():
  try:
    data = request.get_json()
    n = len(data)
    if n > MAX_TRACKS: raise ValueError(f'音轨数太多，最大为{MAX_TRACKS}')

    max_len = 0
    for d in data:
      length = math.ceil(len(d['arr']) / 2) *  2 - 1
      max_len = max(max_len, length)

    if (max_len > MAX_LENGTH): raise ValueError(f'投影超过最长长度，最大为{MAX_LENGTH}')

    l, h, offsets = calculate_grid(n)
    reg = Region(0,0,0,max_len,h,l)

    for i in range(n):
      ox, oy = offsets[i]
      makeTrack(reg, data[i], ox, oy)

    schem = reg.as_schematic(name="Unnamed music", author="mcpixelart.com", description="Create your art of mc online.")
    fname = get_unique_filename()
    schem.save(os.path.join(STATIC_FOLDER, 'music', fname))

    x_ident = request.headers.get('X-IDENT')
    if not x_ident:
        x_ident = ''
    new_art('music', fname,x_ident)
    # 备份
    with gzip.open(os.path.join(STATIC_FOLDER, 'music_backup', fname), 'wb') as f:
      pickle.dump(data, f)
    return jsonify({'url': fname}), 200

  except Exception as e:
    logger.error('musicGen >', str(e))
    return jsonify({'error': f'制作出错'}), 400
