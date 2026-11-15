
# 第一阶段：构建 React 前端
FROM node:22-alpine AS builder

WORKDIR /app

# 先复制依赖清单
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制前端源代码
COPY . .

# 构建生产版本
RUN npm run build


# 第二阶段：使用 Nginx 提供静态文件
FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
