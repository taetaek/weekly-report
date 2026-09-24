import os
from dotenv import load_dotenv

load_dotenv()

# Google Calendar 인증 (Workload Identity Federation을 통한 Application Default Credentials)
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# 캘린더 ID 목록
CALENDAR_IDS = {
    "자기계발_취미": "phr0n4324p0g5d1jn8hp5e9cac@group.calendar.google.com",
    "개인업무": "pofffq28pj9hidjjdbnendj8bk@group.calendar.google.com",
    "자유시간": "lq8b26n6a4gunllrr2em6a0aq4@group.calendar.google.com",
"문화생활": "gnq6n2tfa0eu6qg3p60hn8am5k@group.calendar.google.com",
}

# 자기계발 영역 키워드 (summary에서 검색)
ACTIVITY_KEYWORDS = {
    "영어": ["영어", "잉글리시버디"],
    "경제": ["부동산", "경매", "경제공부"],
    "운동": ["운동", "농구", "클라이밍", "코트메이트", "두스켓볼"],
    "창작&학습": ["WWT", "Gathering", "클로더스", "스터디", "책생각", "독서", "서포테스트"],
    "음악": ["드럼", "캐롤라인"],
}

# 휴식은 자유시간 캘린더로 별도 파악
REST_CALENDAR = "자유시간"

# 흑연 색상 ID (Google Calendar API 기준)
GRAPHITE_COLOR_ID = "8"

# 대시보드
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "")
DASHBOARD_OUTPUT_PATH = os.getenv("DASHBOARD_OUTPUT_PATH", "public/index.html")

TIMEZONE = os.getenv("REPORT_TIMEZONE", "Asia/Seoul")
