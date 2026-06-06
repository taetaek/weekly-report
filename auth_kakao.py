"""
카카오톡 OAuth2 인증 - 최초 1회만 실행하면 됩니다.

1. https://developers.kakao.com 에서 앱 생성
2. 플랫폼 → Web → 사이트 도메인: http://localhost
3. 카카오 로그인 활성화
4. 동의항목 → 카카오톡 메시지 전송 체크
5. 앱 키 → REST API 키를 .env의 KAKAO_REST_API_KEY에 입력
6. 이 스크립트 실행 → 브라우저에서 로그인 → 코드 복사 → 입력
"""

import webbrowser
import requests
from urllib.parse import urlparse, parse_qs
from config import KAKAO_REST_API_KEY

REDIRECT_URI = "http://localhost"
AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
TOKEN_URL = "https://kauth.kakao.com/oauth/token"


def main():
    if not KAKAO_REST_API_KEY:
        print("❌ .env 파일에 KAKAO_REST_API_KEY를 먼저 입력하세요.")
        return

    auth_url = (
        f"{AUTH_URL}?client_id={KAKAO_REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code"
        f"&scope=talk_message"
    )

    print("브라우저가 열립니다. 카카오 계정으로 로그인 후 리다이렉트된 URL을 복사하세요.\n")
    webbrowser.open(auth_url)

    redirected = input("리다이렉트된 전체 URL을 붙여넣으세요: ").strip()

    parsed = urlparse(redirected)
    code = parse_qs(parsed.query).get("code", [None])[0]
    if not code:
        print("❌ URL에서 code를 찾을 수 없습니다.")
        return

    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": KAKAO_REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    data = resp.json()

    if "refresh_token" not in data:
        print(f"❌ 토큰 발급 실패: {data}")
        return

    print("\n✅ 토큰 발급 성공!")
    print(f"Access Token:  {data['access_token']}")
    print(f"Refresh Token: {data['refresh_token']}")
    print("\n👉 .env 파일의 KAKAO_REFRESH_TOKEN에 Refresh Token을 입력하세요.")


if __name__ == "__main__":
    main()
