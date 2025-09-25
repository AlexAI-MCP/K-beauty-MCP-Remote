# 🚀 K-Beauty MCP Server - Google Cloud Run 배포 가이드

## 📋 사전 준비사항

### 1. Google Cloud 계정 및 프로젝트 설정
- Google Cloud 계정 생성 (무료 $300 크레딧 제공)
- 새 프로젝트 생성 또는 기존 프로젝트 사용
- Cloud Run API 활성화
- Artifact Registry API 활성화 (자동으로 활성화됨)

### 2. Google Cloud CLI 설치
```bash
# Windows (PowerShell)
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe

# 설치 후 초기화
gcloud init
gcloud auth login
```

## 🚀 배포 방법 1: Source Deploy (추천 - 가장 간단)

### 단계별 배포
```bash
# 1. 프로젝트 디렉토리로 이동
cd C:\Users\daewoo111\Desktop\k-beauty-mcp-complete

# 2. Cloud Run 배포 (소스 코드에서 직접)
gcloud run deploy k-beauty-mcp \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10

# 3. 배포 URL 확인
gcloud run services describe k-beauty-mcp \
  --platform managed \
  --region asia-northeast1 \
  --format "value(status.url)"
```

## 🚀 배포 방법 2: Docker Container Deploy

### Docker를 사용한 배포
```bash
# 1. 프로젝트 ID 설정
export PROJECT_ID=$(gcloud config get-value project)

# 2. Docker 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/$PROJECT_ID/k-beauty-mcp

# 3. Cloud Run에 배포
gcloud run deploy k-beauty-mcp \
  --image gcr.io/$PROJECT_ID/k-beauty-mcp \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi
```

## ✅ 배포 확인 및 테스트

### 1. Health Check
```bash
# 배포된 URL 가져오기
URL=$(gcloud run services describe k-beauty-mcp --platform managed --region asia-northeast1 --format 'value(status.url)')

# Health check
curl $URL
# 예상 응답: {"status": "healthy", "server": "k-beauty-remote-mcp", "version": "3.0.0"}
```

### 2. MCP Tools 테스트
```bash
# MCP tools 목록 확인
curl -X POST $URL/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# K-Beauty 도구 실행 테스트
curl -X POST $URL/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search_kbeauty_brands",
      "arguments": {
        "brand_name": "The Ordinary"
      }
    }
  }'
```

## 🎯 카카오 플레이 MCP 등록

배포 성공 후:

1. **카카오 플레이 MCP 콘솔**: https://playmcp.kakao.com/console
2. **서버 정보 입력**:
   - 서버명: `K-Beauty Skincare Assistant`
   - 설명: `AI-powered Korean beauty and skincare analysis with comprehensive photo skin scanning and personalized K-Beauty recommendations`
   - 서버 URL: `https://your-cloud-run-url/mcp`
   - 전송 방식: `HTTP/JSON` 또는 `Streamable HTTP`
   - 인증 방식: `없음` (공개 MCP 서버)

## 💰 비용 관리

### Cloud Run 무료 티어
- **무료 한도**: 매월 200만 요청, 40만 GB·초, 20만 vCPU·초
- **과금 기준**: 요청 수, 메모리 사용량, CPU 사용 시간
- **비활성 시간**: 요금 부과 없음 (서버리스 장점)

### 비용 최적화 설정
```bash
# 최소 인스턴스 0 (비활성 시 과금 없음)
gcloud run services update k-beauty-mcp \
  --platform managed \
  --region asia-northeast1 \
  --min-instances 0 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 0.5
```

## 🔧 문제 해결

### 일반적인 오류들
1. **포트 오류**: Cloud Run은 `PORT` 환경변수를 자동 설정
2. **권한 오류**: `gcloud auth login` 실행
3. **API 비활성화**: Cloud Run API 활성화 필요
4. **메모리 부족**: `--memory` 옵션으로 메모리 증가

### 로그 확인
```bash
# 서비스 로그 확인
gcloud logs read --project=$PROJECT_ID \
  --resource-type cloud_run_revision \
  --resource-labels.service_name=k-beauty-mcp
```

## 🛠️ 관리 명령어

```bash
# 서비스 상태 확인
gcloud run services describe k-beauty-mcp --platform managed --region asia-northeast1

# 트래픽 분할 (A/B 테스트)
gcloud run services update-traffic k-beauty-mcp --to-latest --platform managed --region asia-northeast1

# 서비스 삭제 (필요 시)
gcloud run services delete k-beauty-mcp --platform managed --region asia-northeast1
```

## 🎉 배포 완료!

이제 K-Beauty MCP 서버가 Google Cloud Run에서 실행되며:
- ✅ 전세계 어디서나 접근 가능
- ✅ 자동 스케일링 (0부터 10 인스턴스)
- ✅ 비활성 시 과금 없음
- ✅ SSL 인증서 자동 제공
- ✅ 99.95% 가용성 SLA

카카오 플레이 MCP에 등록하여 사용하세요! 🚀✨
