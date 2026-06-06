import os
import pickle
import datetime
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config import GOOGLE_CREDENTIALS_PATH, GOOGLE_TOKEN_PATH, GOOGLE_SCOPES, TIMEZONE


def get_service():
    creds = None

    if os.path.exists(GOOGLE_TOKEN_PATH):
        with open(GOOGLE_TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"credentials.json 파일이 없습니다: {GOOGLE_CREDENTIALS_PATH}\n"
                    "Google Cloud Console에서 OAuth2 credentials를 다운로드하세요."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CREDENTIALS_PATH, GOOGLE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(GOOGLE_TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)


def get_week_range(offset_weeks=1):
    """
    offset_weeks=1 → 저번 주 (Mon~Sun)
    offset_weeks=0 → 이번 주
    """
    tz = pytz.timezone(TIMEZONE)
    today = datetime.datetime.now(tz).date()

    # 이번 주 월요일
    this_monday = today - datetime.timedelta(days=today.weekday())
    # 대상 주 월요일
    target_monday = this_monday - datetime.timedelta(weeks=offset_weeks)
    target_sunday = target_monday + datetime.timedelta(days=6)

    start_dt = tz.localize(datetime.datetime.combine(target_monday, datetime.time.min))
    end_dt = tz.localize(datetime.datetime.combine(target_sunday, datetime.time(23, 59, 59)))

    return start_dt, end_dt, target_monday, target_sunday


def fetch_calendar_events(service, calendar_id, start_dt, end_dt):
    try:
        result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=250,
        ).execute()
        return result.get("items", [])
    except Exception as e:
        print(f"[경고] 캘린더 조회 실패 ({calendar_id}): {e}")
        return []


def fetch_all_events(calendar_ids, offset_weeks=1):
    service = get_service()
    start_dt, end_dt, week_start, week_end = get_week_range(offset_weeks)

    all_events = {}
    for name, cal_id in calendar_ids.items():
        events = fetch_calendar_events(service, cal_id, start_dt, end_dt)
        all_events[name] = events
        print(f"  {name}: {len(events)}개 조회")

    return all_events, week_start, week_end
