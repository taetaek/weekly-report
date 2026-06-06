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
    lines.append(f"📅 [금주 일정 분석 리포트]")
    lines.append(f"{ws}(월) ~ {we}(일)")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━")
    lines.append("📊 자기계발 영역별 현황")
    lines.append("━━━━━━━━━━━━━━━━━")

    counts = analysis["activity_counts"]
    details = analysis["activity_details"]
    zero_cats = analysis["zero_categories"]

    for cat, emoji in CATEGORY_EMOJI.items():
        count = counts.get(cat, 0)
        alert = "🚨 " if count == 0 else ""
        detail_str = ""
        if count > 0 and details.get(cat):
            # 중복 제거 후 키워드 요약
            unique = list(dict.fromkeys(details[cat]))[:3]
            detail_str = " (" + " / ".join(unique[:2]) + ("..." if len(unique) > 2 else "") + ")"
        lines.append(f"{alert}{emoji} {cat}: {count}개{detail_str}")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━")
    lines.append("📅 카테고리 없는 요일")
    lines.append("━━━━━━━━━━━━━━━━━")

    missing = analysis["missing_days"]
    for cal_key, label in CALENDAR_LABEL.items():
        days = missing.get(cal_key, [])
        if days:
            lines.append(f"• {label} 없음: {', '.join(days)}")
        else:
            lines.append(f"• {label}: 매일 있음 ✅")

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━")
    graphite = analysis["graphite_count"]
    alert = "🚨 " if graphite > 0 else "✅ "
    lines.append(f"{alert}⬛ 미실행 일정 (흑연): {graphite}개")
    lines.append("━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)
