# 使用官方 Python 运行环境（带常用构建工具）
FROM python:3.12-slim

# 安装系统依赖（Playwright 运行所需）
RUN apt-get update && \
    apt-get install -y wget gnupg curl ca-certificates fonts-liberation libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 \
    libnspr4 libnss3 libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    libu2f-udev libvulkan1 libxss1 libgtk-3-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 拷贝项目文件
COPY . .

# 安装依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install playwright && \
    playwright install --with-deps

# 运行主程序
CMD ["python3", "main.py"]
