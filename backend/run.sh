#!/bin/bash

# 1. 进入项目根目录 (根据实际路径修改)
cd "$(dirname "$0")"

# 2. 定义变量
APP_NAME="mcpixelart-server"
PORT=3100
WORKERS=10  # 推荐公式: (2 * CPU核心数) + 1
VENV_PATH="./venv/bin/activate"

echo "正在启动 $APP_NAME 端口: $PORT..."

# 3. 激活虚拟环境
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
else
    echo "错误: 未找到虚拟环境，请先创建 venv"
    exit 1
fi

# 4. 检查端口是否被占用，如果占用则先清理
PID=$(lsof -t -i:$PORT)
if [ ! -z "$PID" ]; then
    echo "端口 $PORT 已被占用 (PID: $PID)，正在清理..."
    kill -9 $PID
fi

# 5. 启动 Gunicorn
gunicorn --daemon \
         --name $APP_NAME \
         --workers $WORKERS \
         --bind 0.0.0.0:$PORT \
         --access-logfile ./access.log \
         --error-logfile ./error.log \
         --capture-output \
         compose:app

if [ $? -eq 0 ]; then
    echo "✅ 启动成功"
else
    echo "❌ 启动失败"
fi
