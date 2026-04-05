# 创建虚拟环境
python3 -m venv venv
# 激活并安装依赖
source venv/bin/activate
pip install -r requirements.txt
# 生产环境必须安装 gunicorn
pip install gunicorn
