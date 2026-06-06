import datetime


CATEGORY_EMOJI = {
    "영어": "🗣",
    "경제": "💰",
    "운동": "🏃",
    "창작&학습": "📚",
    "음악": "🎵",
    "휴식": "🛋",
}

CALENDAR_LABEL = {
    "개인업무": "개인업무",
    "자기계발_취미": "자기계발·취미",
    "자유시간": "자유시간",
}


def build_message(analysis, week_start, week_end):
    lines = []

    ws = week_start.strftime("%Y.%m.%d")
    we = week_end.strftime("%Y.%m.%d")
    lines.append(f"📅 [일정 리포트]")
    lines.append(f"{ws}(월) ~ {we}(일)")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━")
    lines.append("📊 이번주 일정")
    lines.append("━━━━━━━━━━━━━━━━━")

    counts = analysis["activity_counts"]
    details = analysis["activity_details"]
    zero_cats = analysis["zero_categories"]

    for cat, emoji in CATEGORY_EMOJI.items():
        count = counts.get(cat, 0)
        alert = "🚨 " if count == 0 else ""
        lines.append(f"{alert}{emoji} {cat}: {count}건")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━")
    lines.append("📅 일정 없는 요일")
    lines.append("━━━━━━━━━━━━━━━━━")

    all_weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    active_days = analysis["active_days"]
    empty_days = [d for d in all_weekdays if d not in active_days]
    if empty_days:
        lines.append(f"• {', '.join(empty_days)}")
    else:
        lines.append("• 매일 있음 ✅")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━")
    graphite = analysis["graphite_count"]
    cats = analysis.get("graphite_categories", set())
    cat_str = f" ({'/'.join(sorted(cats))})" if cats else ""
    lines.append(f"{alert}⬛ 저번주 미실행 일정: {graphite}건{cat_str}")
    lines.append("━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)
