# 주간 일정 분석 & 카카오톡 알림 설정 가이드

## 1단계 — Python 패키지 설치

```powershell
cd D:\weekly-report
pip install -r requirements.txt
```

---

## 2단계 — Google Calendar API 인증

### 2-1. Google Cloud Console 설정
1. https://console.cloud.google.com 접속
2. 새 프로젝트 생성 (예: `weekly-report`)
3. **API 및 서비스 → 라이브러리** → "Google Calendar API" 검색 후 활성화
4. **API 및 서비스 → 사용자 인증 정보**
   - `+ 사용자 인증 정보 만들기` → OAuth 클라이언트 ID
   - 애플리케이션 유형: **데스크톱 앱**
   - 생성 후 JSON 다운로드
5. 다운로드한 파일을 `credentials/credentials.json`으로 저장

### 2-2. 최초 인증 (1회만)
```powershell
python main.py --dry-run
```
브라우저가 열리면 Google 계정으로 로그인 → 권한 허용  
`credentials/token.pickle` 파일이 생성되면 완료.

---

## 3단계 — 카카오톡 API 설정

### 3-1. 카카오 개발자 앱 생성
1. https://developers.kakao.com 접속 → 내 애플리케이션 → 애플리케이션 추가
2. **플랫폼 설정** → Web → 사이트 도메인: `http://localhost`
3. **카카오 로그인** → 활성화 ON, Redirect URI: `http://localhost`
4. **동의항목** → 카카오톡 메시지 전송 → 필수 동의 설정
5. **앱 키** → REST API 키 복사

### 3-2. .env 파일 설정
```powershell
Copy-Item .env.example .env
notepad .env
```
`.env` 파일에서 `KAKAO_REST_API_KEY`에 REST API 키 입력 후 저장.

### 3-3. 카카오 토큰 발급 (1회만)
```powershell
python auth_kakao.py
```
브라우저에서 로그인 → 리다이렉트된 URL 복사 → 붙여넣기  
출력된 **Refresh Token**을 `.env`의 `KAKAO_REFRESH_TOKEN`에 입력.

---

## 4단계 — 테스트 실행

```powershell
# 카카오톡 전송 없이 터미널에서만 확인
python main.py --dry-run

# 실제 카카오톡 전송
python main.py
```

---

## 5단계 — Windows 작업 스케줄러 등록 (매주 월요일 08:00)

PowerShell을 **관리자 권한**으로 열고:
```powershell
cd D:\weekly-report
.\setup_scheduler.ps1
```

등록 확인:
```powershell
Get-ScheduledTask -TaskName "WeeklyCalendarReport"
```

---

## 분석 기준

| 영역 | 키워드 |
|------|--------|
| 영어 | 영어, 잉글리시버디 |
| 경제 | 부동산, 경매, 경제공부 |
| 운동 | 농구, 클라이밍, 코트메이트, 두스켓볼 |
| 창작&학습 | WWT, Gathering, 클로더스, 스터디, 책생각, 독서 |
| 음악 | 드럼, 캐롤라인 |
| 휴식 | 자유시간 캘린더 전체 |

- 각 영역 **0개**이면 🚨 알림 표시
- **흑연(colorId=8)** 색상 일정 = 미실행 일정으로 집계
- 개인업무·자기계발·취미·자유시간 캘린더가 **없는 요일** 표시
