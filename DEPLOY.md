# K-Beauty Remote MCP Server 배포 가이드

## 🌐 리모트 MCP 서버로 변환 완료!

이제 로컬 stdio 기반 MCP 서버가 **HTTP/SSE 기반 리모트 MCP 서버**로 변환되었습니다.

## 📁 추가된 파일들

- `http_server.py` - FastAPI 기반 HTTP MCP 서버
- `Dockerfile` - 컨테이너화를 위한 Docker 설정
- `docker-compose.yml` - 서비스 오케스트레이션
- `requirements.txt` - 업데이트된 의존성

## 🚀 배포 옵션들

### 1. 로컬 테스트
```bash
# 의존성 설치
pip install -r requirements.txt

# HTTP 서버 실행 
python http_server.py

# 또는 uvicorn으로 실행
uvicorn http_server:app --host 0.0.0.0 --port 8000 --reload
```

서버가 실행되면:
- `http://localhost:8000/` - Health check
- `http://localhost:8000/mcp` - MCP SSE endpoint  
- `POST http://localhost:8000/mcp` - MCP Streamable HTTP endpoint

### 2. Docker로 배포
```bash
# Docker 이미지 빌드
docker build -t k-beauty-mcp .

# 컨테이너 실행
docker run -p 8000:8000 k-beauty-mcp

# 또는 docker-compose 사용
docker-compose up -d
```

### 3. 클라우드 배포 옵션

#### A. **Heroku** (가장 간단)
```bash
# Heroku CLI 설치 후
heroku create k-beauty-mcp-server
heroku container:push web
heroku container:release web
heroku open
```

#### B. **Google Cloud Run** (추천)
```bash
# Cloud Build로 배포
gcloud run deploy k-beauty-mcp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### C. **Railway** (개발자 친화적)
1. [Railway](https://railway.app) 계정 생성
2. GitHub 레포 연결
3. 자동 배포 시작

#### D. **Render** (무료 티어 제공)
1. [Render](https://render.com) 계정 생성
2. 웹 서비스로 배포
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn http_server:app --host 0.0.0.0 --port $PORT`

### 4. 카카오 플레이 MCP 등록

배포 후 얻은 URL을 사용해서 카카오 플레이 MCP에 등록:

1. **서버 URL**: `https://your-domain.com/mcp`
2. **전송 방식**: HTTP/SSE 또는 Streamable HTTP
3. **인증 방식**: 필요시 OAuth 설정

## 🔧 서버 특징

### 지원하는 전송 방식
- ✅ **SSE (Server-Sent Events)**: `GET /mcp`
- ✅ **Streamable HTTP**: `POST /mcp` 
- ✅ **레거시 HTTP+SSE**: `POST /messages`

### 세션 관리
- 자동 세션 생성 및 관리
- 세션별 상태 추적
- Heartbeat으로 연결 유지

### 기존 기능 유지
- 모든 K-Beauty 도구 동일하게 작동
- 피부 분석, 제품 추천, 성분 분석 등
- 웹 검색 요청 기능

## 🧪 테스트 방법

### MCP Inspector로 테스트
```bash
# MCP Inspector 실행
npm install -g @anthropics/mcp-inspector
mcp-inspector

# 브라우저에서 localhost:5173 접속
# 서버 URL에 http://localhost:8000/mcp 입력
```

### 수동 테스트
```bash
# Health check
curl http://localhost:8000/

# Tools 목록 가져오기
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

## 🔒 보안 고려사항

### 프로덕션 배포 시 필수 설정
- CORS 도메인 제한
- HTTPS 사용 (Let's Encrypt 등)
- 환경 변수로 민감 정보 관리
- Rate limiting 적용
- 로깅 및 모니터링 설정

### OAuth 인증 (선택사항)
필요시 `http_server.py`의 OAuth 관련 코드를 확장하여 사용자 인증을 구현할 수 있습니다.

## 📊 모니터링

### Health Check
서버 상태 확인: `GET /`

### 로그 확인
```bash
# Docker 컨테이너 로그
docker logs -f container_name

# 또는 직접 실행 시 콘솔 출력 확인
```

이제 K-Beauty MCP 서버가 완전한 리모트 MCP 서버로 변환되었습니다! 🎉

어떤 배포 방식을 선택하시겠나요?
