FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 安装 mysqlclient 编译所需的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install --no-cache-dir uv

# 先复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装项目运行依赖
RUN uv sync --frozen --no-dev --no-install-project

# 复制项目代码
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

# 收集静态文件
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]