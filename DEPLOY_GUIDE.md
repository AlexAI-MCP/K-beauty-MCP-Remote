# K-Beauty MCP Server 배포 가이드

## 🚀 Railway 배포 (권장)

### 1단계: GitHub 리포지토리 생성

1. GitHub 계정에 로그인 (https://github.com)
2. 새 리포지토리 생성:
   - 리포지토리 이름: `k-beauty-mcp-server`
   - 설명: `AI-powered Korean Beauty and Skincare MCP Server`
   - Public으로 설정
   - README, .gitignore, License 체크하지 않음

### 2단계: 코드를 GitHub에 업로드

로컬에서 다음 명령어 실행:

```bash
cd C:\Users\daewoo111\Desktop\k-beauty-mcp-complete

# Git 초기화
git init

# .gitignore 파일 생성 (이미 존재하면 skip)
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: K-Beauty Remote MCP Server"

# GitHub 리포지토리 연결 (YOUR_USERNAME을 실제 GitHub 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/k-beauty-mcp-server.git

# 업로드
git branch -M main
git push -u origin main
```

### 3단계: Railway 배포

1. Railway 계정 생성: https://railway.app
2. GitHub 계정으로 로그인
3. "Deploy from GitHub repo" 클릭
4. 방금 생성한 `k-beauty-mcp-server` 리포지토리 선택
5. 자동 배포 시작!

### 4단계: 공개 URL 생성

1. 배포 완료 후 프로젝트 대시보드로 이동
2. Settings → Networking
3. "Generate Domain" 클릭
4. 생성된 URL 확인 (예: `https://k-beauty-mcp-server-production-xxxx.up.railway.app`)

### 5단계: MCP 서버 테스트

생성된 URL로 테스트:
- Health Check: `https://your-domain/`
- MCP SSE: `https://your-domain/mcp`
- MCP HTTP: `POST https://your-domain/mcp`

### 6단계: 카카오 플레이 MCP 등록

1. https://playmcp.kakao.com/console 접속
2. "새 MCP 서버 추가" 클릭
3. 서버 정보 입력:
   - **서버명**: `K-Beauty Skincare Assistant`
   - **설명**: `AI-powered Korean beauty and skincare analysis with photo skin scanning`
   - **서버 URL**: `https://your-domain/mcp`
   - **전송 방식**: `HTTP/SSE` 또는 `Streamable HTTP`
   - **인증**: 없음 (공개 서버)

## 🌟 다른 배포 옵션들

### Google Cloud Run 배포
```bash
gcloud run deploy k-beauty-mcp \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Render 배포
1. Render.com 계정 생성
2. "New Web Service" 클릭
3. GitHub 리포지토리 연결
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn http_server:app --host 0.0.0.0 --port $PORT`

### Docker 기반 배포 (Heroku, DigitalOcean 등)
```bash
# Docker 이미지 빌드
docker build -t k-beauty-mcp .

# 컨테이너 실행 테스트
docker run -p 8000:8000 k-beauty-mcp

# 클라우드 플랫폼에 푸시
```

## 🔧 트러블슈팅

### Railway 빌드 실패 시
- `requirements.txt` 의존성 확인
- `runtime.txt`에 Python 버전 명시
- `railway.json` 설정 확인

### CORS 오류 발생 시
`http_server.py`에서 CORS 설정 수정:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://playmcp.kakao.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 메모리 부족 오류 시
Railway 플랜 업그레이드 또는 다른 플랫폼 사용 고려

## 📊 모니터링 및 로그

Railway에서는:
- 빌드 로그: 배포 탭에서 확인
- 런타임 로그: 메트릭 탭에서 확인
- 에러 추적: 로그에서 Python 에러 확인

이제 K-Beauty MCP 서버가 전세계 어디서든 접근 가능한 리모트 MCP가 되었습니다! 🌍✨
