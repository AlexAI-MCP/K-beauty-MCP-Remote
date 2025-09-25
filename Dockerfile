# Dockerfile for K-Beauty Remote MCP Server
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 파일들 복사
COPY server.py .
COPY http_server.py .
COPY README.md .
COPY PHOTO_ANALYSIS_GUIDE.md .

# 환경 변수 설정
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app

# 포트 노출
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 앱 실행
CMD ["uvicorn", "http_server:app", "--host", "0.0.0.0", "--port", "8000"]
