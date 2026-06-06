import os
from dotenv import load_dotenv

load_dotenv()

# Google Calendar 인증
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials/credentials.json")
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "credentials/token.pickle")
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
    "운동": ["농구", "클라이밍", "코트메이트", "두스켓볼"],
    "창작&학습": ["WWT", "Gathering", "클로더스", "스터디", "책생각", "독서"],
    "음악": ["드럼", "캐롤라인"],
}

# 휴식은 자유시간 캘린더로 별도 파악
REST_CALENDAR = "자유시간"

# 흑연 색상 ID (Google Calendar API 기준)
GRAPHITE_COLOR_ID = "8"

# 카카오톡
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")
KAKAO_REFRESH_TOKEN = os.getenv("KAKAO_REFRESH_TOKEN", "")
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_SEND_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

TIMEZONE = os.getenv("REPORT_TIMEZONE", "Asia/Seoul")
