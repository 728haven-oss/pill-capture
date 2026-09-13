# 알약캡쳐

알약 사진 한 장(또는 실시간 카메라·동영상)으로 **같은 종류끼리 묶어 개수만** 세어 주는 앱. 약품 식별은 하지 않으며 사진은 기기 밖으로 나가지 않습니다.

- 소스: `src/app.html` (단일 HTML, 외부 라이브러리 없음)
- 빌드: `python3 tools/build.py` → `docs/` (PWA + Capacitor webDir)
- 안드로이드/iOS: Capacitor 6 래핑. 네이티브 프로젝트는 CI에서 생성되므로 저장소에 없음.

## 받는 방법

| 대상 | 방법 |
|---|---|
| 안드로이드 테스트 | [Releases → latest](../../releases/tag/latest) 의 `pill-capture-debug.apk` 설치 (main 푸시마다 자동 갱신) |
| 플레이스토어 제출 | 태그 `v1.0.0` 푸시 → **Android Release (Play)** 가 서명 AAB 생성 (시크릿 필요, 워크플로 주석 참고) |
| 아이폰 (스토어 전) | GitHub Pages 주소를 Safari로 열고 공유 → 홈 화면에 추가 |
| 앱스토어/TestFlight | 태그 푸시 → **iOS (App Store)** 워크플로 (Apple 개발자 계정 시크릿 필요) |

## 스토어 등록 시 필요한 것

- Google Play 개발자 계정, 업로드 키스토어(`android-release.yml` 주석의 keytool 명령), 개인정보처리방침 URL(`store/privacy.html` 이 Pages에 `privacy.html` 로 함께 배포됨)
- Apple 개발자 계정($99/년), 배포 인증서(.p12), App Store 프로비저닝 프로파일(Bundle ID `kr.pillcapture.app`), App Store Connect API 키
- 카메라 권한 문구는 CI가 Info.plist / AndroidManifest 에 자동 삽입
