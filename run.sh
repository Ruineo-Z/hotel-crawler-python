#!/bin/bash

# 创建python虚拟环境，并激活
python3 -m venv .venv
source .venv/bin/activate

# 安装python第三方依赖库
pip install -r requirements.txt

# 安装playwright依赖
pip install playwright
playwright install

# 运行定时任务脚本
python3 main.py