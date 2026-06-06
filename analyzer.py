import datetime
import pytz
from config import ACTIVITY_KEYWORDS, GRAPHITE_COLOR_ID, REST_CALENDAR, TIMEZONE

WEEKDAY_NAMES = ["월", "화", "수", "목", "금", "토", "일"]


def get_event_date(event):
    start = event.get("start", {})
    date_str = start.get("dateTime") or start.get("date", "")
    if not date_str:
        return None
    date_part = date_str[:10]
    return datetime.date.fromisoformat(date_part)


def get_weekday_name(date):
    return WEEKDAY_NAMES[date.weekday()]


def classify_activity(summary):
    summary_lower = summary.lower()
    matched = []
    for category, keywords in ACTIVITY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in summary_lower:
                matched.append(category)
                break
    return matched


def analyze(all_events_by_calendar):
    activity_counts = {cat: 0 for cat in ACTIVITY_KEYWORDS}
    activity_counts["휴식"] = 0

    # 카테고리별 이벤트 이름 수집 (상세 출력용)
    activity_details = {cat: [] for cat in ACTIVITY_KEYWORDS}
    activity_details["휴식"] = []

    graphite_count = 0
    graphite_events = []
    graphite_categories = set()

    # 요일별 카테고리 유무
    days_with = {
        "개인업무": set(),
        "자기계발_취미": set(),
        "자유시간": set(),
    }
    active_days = set()  # 활동이 1건 이상 있는 요일

    for cal_name, events in all_events_by_calendar.items():
        for event in events:
            summary = event.get("summary", "")
            color_id = event.get("colorId", "")
            event_date = get_event_date(event)
            if event_date is None:
                continue
            weekday = get_weekday_name(event_date)

            # 흑연 색상 (미실행) 카운트
            if color_id == GRAPHITE_COLOR_ID:
                graphite_count += 1
                graphite_events.append(summary)
                if "일정" not in summary:
                    for cat in classify_activity(summary):
                        graphite_categories.add(cat)

            # 요일별 카테고리 체크
            if cal_name in days_with:
                days_with[cal_name].add(weekday)

            # 자유시간 캘린더 → 휴식
            if cal_name == REST_CALENDAR:
                activity_counts["휴식"] += 1
                activity_details["휴식"].append(summary)
                active_days.add(weekday)
                continue

            # 키워드 기반 분류 (자기계발_취미, 개인업무 모두 검색)
            if "일정" in summary:
                continue
            matched_categories = classify_activity(summary)
            for cat in matched_categories:
                activity_counts[cat] += 1
                activity_details[cat].append(summary)
            if matched_categories:
                active_days.add(weekday)

    all_weekdays = set(WEEKDAY_NAMES)
    missing_days = {
        "개인업무": sorted(all_weekdays - days_with["개인업무"], key=WEEKDAY_NAMES.index),
        "자기계발_취미": sorted(all_weekdays - days_with["자기계발_취미"], key=WEEKDAY_NAMES.index),
        "자유시간": sorted(all_weekdays - days_with["자유시간"], key=WEEKDAY_NAMES.index),
    }

    zero_categories = [cat for cat, cnt in activity_counts.items() if cnt == 0]

    return {
        "activity_counts": activity_counts,
        "activity_details": activity_details,
        "graphite_count": graphite_count,
        "graphite_events": graphite_events,
        "graphite_categories": graphite_categories,
        "missing_days": missing_days,
        "zero_categories": zero_categories,
        "active_days": active_days,
    }
