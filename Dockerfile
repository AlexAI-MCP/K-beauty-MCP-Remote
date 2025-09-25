# Google Cloud Run용 Dockerfile
FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=True
ENV APP_HOME=/app
WORKDIR $APP_HOME

# 시스템 의존성 업데이트
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 먼저 복사하고 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# Cloud Run은 PORT 환경 변수를 자동으로 설정함
# 포트 8080이 기본값이지만 $PORT를 사용하는 것이 권장됨
EXPOSE 8080

# FastAPI 애플리케이션 실행
# Cloud Run에서 제공하는 PORT 환경변수 사용
CMD uvicorn http_server:app --host 0.0.0.0 --port $PORT
