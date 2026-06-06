"""
주간 일정 분석 & 카카오톡 알림 메인 스크립트
매주 월요일 오전 8시 자동 실행 (Windows 작업 스케줄러)
"""

import sys
from config import CALENDAR_IDS
from calendar_fetch import fetch_all_events
from analyzer import analyze
from message_builder import build_message
from kakao_notify import send_message


def run(dry_run=False):
    print("=" * 50)
    print("📅 주간 일정 분석 시작")
    print("=" * 50)

    print("\n[1/4] 이번 주 일정 가져오는 중...")
    all_events, week_start, week_end = fetch_all_events(CALENDAR_IDS, offset_weeks=0)

    print("\n[2/4] 일정 분석 중...")
    result = analyze(all_events)

    print("  저번 주 미실행 일정 확인 중...")
    last_events, _, _ = fetch_all_events(CALENDAR_IDS, offset_weeks=1)
    last_result = analyze(last_events)
    result["graphite_count"] = last_result["graphite_count"]
    result["graphite_events"] = last_result["graphite_events"]
    result["graphite_categories"] = last_result["graphite_categories"]

    print("\n[3/4] 리포트 메시지 생성 중...")
    message = build_message(result, week_start, week_end)

    print("\n" + "=" * 50)
    print(message)
    print("=" * 50)

    if dry_run:
        print("\n[dry-run 모드] 카카오톡 전송 생략")
        return

    print("\n[4/4] 카카오톡 전송 중...")
    try:
        send_message(message)
        print("✅ 카카오톡 전송 완료!")
    except Exception as e:
        print(f"❌ 카카오톡 전송 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or "-d" in sys.argv
    run(dry_run=dry)
