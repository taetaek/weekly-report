import json
import requests
from config import KAKAO_REST_API_KEY, KAKAO_CLIENT_SECRET, KAKAO_REFRESH_TOKEN, KAKAO_TOKEN_URL, KAKAO_SEND_URL


def refresh_access_token():
    """Refresh token으로 새 Access Token 발급"""
    if not KAKAO_REFRESH_TOKEN:
        raise ValueError(
            "KAKAO_REFRESH_TOKEN이 설정되지 않았습니다.\n"
            "auth_kakao.py를 먼저 실행하여 토큰을 발급받으세요."
        )

    resp = requests.post(
        KAKAO_TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": KAKAO_REST_API_KEY,
            "client_secret": KAKAO_CLIENT_SECRET,
            "refresh_token": KAKAO_REFRESH_TOKEN,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()
    data = resp.json()

    if "access_token" not in data:
        raise RuntimeError(f"Access Token 발급 실패: {data}")

    return data["access_token"]


def send_message(text):
    """카카오톡 나에게 보내기"""
    if not KAKAO_REST_API_KEY:
        raise ValueError("KAKAO_REST_API_KEY가 설정되지 않았습니다.")

    access_token = refresh_access_token()

    template = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "https://calendar.google.com",
            "mobile_web_url": "https://calendar.google.com",
        },
        "button_title": "캘린더 열기",
    }

    resp = requests.post(
        KAKAO_SEND_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"template_object": json.dumps(template, ensure_ascii=False)},
    )

    if resp.status_code != 200:
        raise RuntimeError(f"카카오톡 전송 실패 ({resp.status_code}): {resp.text}")

    result = resp.json()
    if result.get("result_code") != 0:
        raise RuntimeError(f"카카오톡 전송 오류: {result}")

    return True
