#!/bin/bash

PORT=3100
echo "正在停止端口 $PORT 上的 Flask 服务..."

# 查找占用该端口的进程 ID
PID=$(lsof -t -i:$PORT)

if [ -z "$PID" ]; then
    echo "⚠️ 未发现正在运行的服务。"
else
    # 优雅关闭进程
    kill $PID
    sleep 2
    echo "✅ 服务已停止。"
fi
