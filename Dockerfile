# 使用官方 Python 运行环境
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

# 创建Chrome安装脚本
RUN echo '#!/bin/bash\n\
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg\n\
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list\n\
apt-get update\n\
apt-get install -y google-chrome-stable\n\
echo "Chrome安装完成"' > /app/install_chrome.sh && \
    chmod +x /app/install_chrome.sh

# 设置环境变量
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome
ENV DISPLAY=:99

# 运行主程序
CMD ["/app/install_chrome.sh", "&&", "python3", "main.py"]