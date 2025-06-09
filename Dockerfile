# 使用带有更多依赖的基础镜像
FROM python:3.12

# 设置工作目录
WORKDIR /app

# 拷贝项目文件
COPY . .

# 安装依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install playwright && \
    playwright install && \
    playwright install-deps

# 运行主程序
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]