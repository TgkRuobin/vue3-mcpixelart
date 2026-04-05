from flask import Blueprint, request

import json
from datetime import datetime

error_bp = Blueprint('error', __name__)

LOG_FILE = 'error_log.jsonl'

# 错误上报
@error_bp.route('/', methods=['POST'])
def post_err():
  try:
    data = request.get_json()
    if data is not None:
      data['server_time'] = str(datetime.now())
      data['user'] = request.headers.get('X-IDENT', '')
      with open(LOG_FILE, 'ab') as f:
        json_line = (json.dumps(data) + '\n').encode('utf-8')
        f.write(json_line)

    return 'OK', 200

  except Exception as e:
    print(str(e))
    return 'Not recorded', 200
