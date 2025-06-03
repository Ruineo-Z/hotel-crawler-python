# 使用带有更多依赖的基础镜像
FROM python:3.12

# 设置工作目录
WORKDIR /app

# 安装Chrome依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    procps \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 拷贝项目文件
COPY . .

# 安装依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install playwright && \
    playwright install && \ 
    playwright install-deps

# 运行主程序
CMD ["python3", "main.py"]