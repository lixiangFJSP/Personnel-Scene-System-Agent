FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build && \
    cp -r /app/无感考勤看板文件 /app/dist/ && \
    cp -r /app/劳保穿戴看板文件 /app/dist/ && \
    cp -r /app/作业组合看板文件 /app/dist/ && \
    cp -r /app/工时统计看板文件 /app/dist/

FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
