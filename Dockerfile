# ===== Stage 1: 构建前端 =====
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build && \
    cp -r 无感考勤看板文件 dist/ && \
    cp -r 劳保穿戴看板文件 dist/ && \
    cp -r 作业组合看板文件 dist/ && \
    cp -r 工时统计看板文件 dist/

# ===== Stage 2: 最终镜像 (nginx + Python backend) =====
FROM python:3.12-slim

# 使用阿里云 Debian 镜像源加速
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        nginx \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖（使用阿里云 pip 镜像）
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
    -r /app/backend/requirements.txt

# 拷贝前端构建产物
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# 拷贝后端代码
COPY backend/ /app/backend/

# 拷贝 nginx 配置（覆盖默认）
RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 拷贝 supervisord 配置
COPY supervisord.conf /etc/supervisord.conf

# 创建数据目录（用于持久化 llm_config.json）
RUN mkdir -p /app/data && chmod 777 /app/data

# 暴露端口
EXPOSE 80

# supervisord 同时管理 nginx 和 uvicorn
CMD ["supervisord", "-c", "/etc/supervisord.conf", "-n"]
