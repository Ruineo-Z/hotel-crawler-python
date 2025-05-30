# 优化后的Dockerfile
FROM python:3.12-slim

# 安装Chrome和依赖
RUN apt-get update && \
    apt-get install -y wget gnupg curl ca-certificates && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get install -y fonts-liberation libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 \
    libnss3 libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    libu2f-udev libvulkan1 libxss1 libgtk-3-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置显示环境变量（用于无头模式）
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROME_PATH=/usr/bin/google-chrome

WORKDIR /app
COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install playwright && \
    playwright install --with-deps

CMD ["python3", "main.py"]