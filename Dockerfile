# 使用 Python 3.10 的官方镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir data tmp
RUN mkdir data/quizs data/students

# 复制应用代码
COPY . .