# agm_lpac_attendance -- Fly.io 用 Dockerfile
# Flask + Flask-SQLAlchemy + Flask-Login + Flask-Mail + gunicorn

FROM python:3.12-slim

# tini で SIGTERM を gunicorn に正しく届ける + ca-certificates で SSL 検証
RUN apt-get update \
    && apt-get install -y --no-install-recommends tini ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    TZ=Asia/Tokyo

# 依存だけ先にコピーしてビルドキャッシュを効かせる
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体
COPY . .

EXPOSE 8080

ENTRYPOINT ["/usr/bin/tini", "--"]

# gunicorn で app.py の Flask app を起動
# - 1 worker / threads 4 で 256MB に収める（同時接続は threads でさばく）
# - timeout 60 秒（CSV インポート等のため少し余裕）
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "1", \
     "--threads", "4", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
