#!/bin/bash
# 金银市场分析平台 - Linux/Mac启动脚本

echo "============================================"
echo "金银市场数据分析平台 启动脚本"
echo "============================================"
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python"
    exit 1
fi

# 进入backend目录
echo "[1/4] 进入后端目录..."
cd backend

# 安装依赖
echo "[2/4] 安装Python依赖..."
pip3 install -r requirements.txt -q

# 初始化数据库
echo "[3/4] 初始化数据库..."
python3 models.py

# 启动Flask应用
echo "[4/4] 启动Flask API服务器 (http://localhost:5000)..."
echo
echo "Flask服务器已启动！"
echo
echo "请在另一个终端窗口运行:"
echo "  cd frontend"
echo "  python3 -m http.server 8000"
echo
echo "然后在浏览器访问: http://localhost:8000"
echo

python3 app.py
