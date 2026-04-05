from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request

import gzip
import io

app = Flask(__name__)

from .user import user_bp
from .error import error_bp
from .pixelart import pixelart_bp
from .music import music_bp
from .enhance import enhance_bp
from .share import share_bp

app.register_blueprint(user_bp)
app.register_blueprint(error_bp)
app.register_blueprint(pixelart_bp)
app.register_blueprint(music_bp)
app.register_blueprint(enhance_bp)
app.register_blueprint(share_bp)

@app.before_request
def auto_decompress_middleware():
    """
    透明解压中间件：
    如果检测到 X-Encode: gzip，则在进入路由函数前静默解压数据。
    """
    if request.headers.get('X-Encode') == 'gzip' and request.get_data():
        try:
            compressed_data = request.get_data()

            with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as f:
                decompressed_data = f.read()

            request._cached_data = decompressed_data

            request.environ['CONTENT_TYPE'] = 'application/json'
            request.environ['CONTENT_LENGTH'] = str(len(decompressed_data))

        except Exception as e:
            print(f"Decompression failed: {e}")
            return {'error': '数据解压失败'}, 500
    