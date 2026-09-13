# 알약캡쳐 스토어 등록 자료

공통
- 앱 이름: 알약캡쳐
- 패키지/Bundle ID: kr.pillcapture.app
- 카테고리: 의료 (Medical) — 대안: 도구/유틸리티
- 개인정보처리방침 URL: https://728haven-oss.github.io/pill-capture/privacy.html
- 지원/마케팅 URL: https://github.com/728haven-oss/pill-capture
- 지원 이메일: 728haven@gmail.com
- 아이콘: assets/icons/icon-512.png (Play), icon-1024.png (App Store) — tools/make_icons.py 로 생성
- 스크린샷: Play 1079×2397, iPhone 6.7" 1290×2796 (세션에서 전달한 zip)

---

## Google Play

짧은 설명 (80자 이내)
> 알약 사진 한 장으로 종류별 개수를 바로 확인. 사진은 기기 밖으로 나가지 않습니다.

전체 설명
> 알약캡쳐는 약국·조제실에서 알약 개수를 빠르게 확인하기 위한 앱입니다.
>
> 트레이나 흰 종이 위에 알약을 펼쳤 놓고 촬영하면, 같은 종류끼리 자동으로 묶어 종류별 개수와 합계를 보여줍니다. 약품명을 식별하는 앱이 아니라 "몇 개인지"만 세어 주는 도구입니다.
>
> 주요 기능
> • 사진 카운팅: 촬영하거나 갤러리 사진을 고르면 종류별로 색 테두리를 씌우고 개수를 표시
> • 실시간 카운팅: 카메라를 비추는 동안 계속 세고, 원하는 순간 "이 장면 고정"으로 확정
> • 동영상 파일 카운팅: 저장된 영상을 불러와 장면별로 확인
> • 혼합 / 한 종류 모드: 여러 종류가 섞여 있으면 자동 분류, 한 종류만 있으면 총 개수만
> • 분류 민감도 조절, 잘못 나뉜 종류 합치기, +/− 수동 보정, 결과 텍스트 복사
>
> 개인정보
> 사진·영상은 기기 안에서만 분석되며 서버로 전송되거나 저장되지 않습니다. 회원가입·로그인이 없고, 광고와 분석 도구를 사용하지 않습니다.
>
> 정확도 안내
> 알약이 겹치지 않게 펼치고, 단색 배경에서 그림자가 적은 조명으로 위에서 수직 촬영할 때 가장 정확합니다. 겹친 알약은 크기로 추정하므로 화면에서 바로 보정할 수 있습니다. 조제 검수의 보조 도구이며 최종 확인은 약사가 직접 해야 합니다.

데이터 보안(Data safety) 설문 답변
- 데이터 수집: 아니요 (카메라 이미지는 기기 내에서만 처리, 전송·저장 없음)
- 데이터 공유: 아니요
- 암호화 전송: 해당 없음 (전송 데이터 없음)
- 데이터 삭제 요청: 해당 없음
- 권한: CAMERA — 알약 촬영·실시간 카운팅. 사진 선택은 시스템 사진 선택기 사용(별도 저장소 권한 불필요)

콘텐츠 등급 설문: 폭력·성적 내용·약물 홍보 없음 → 전체이용가(3+). "의료 앱" 여부: 진단·치료 조언을 제공하지 않음(개수 세기 도구).
타겟 연령: 18세 이상(약사·약국 직원). 어린이 대상 아님.
광고 포함: 없음. 앱 내 구매: 없음.
의료 앱 정책 관련 메모: 약품 식별·복약 지도·진단 기능 없음. 설명에 "보조 도구, 최종 확인은 약사" 문구 포함.

---

## App Store (App Store Connect)

- 이름: 알약캡쳐
- 부제(30자): 종류별 알약 개수, 사진 한 장으로
- 프로모션 텍스트(170자): 트레이 위 알약을 찍으면 같은 종류끼리 묶어 개수를 세어 줍니다. 실시간 카메라·동영상도 지원. 사진은 기기 밖으로 나가지 않습니다.
- 키워드(100자): 알약,카운팅,약국,조제,개수,세기,pill,counter,count,pharmacy,tablet
- 설명: (Google Play 전체 설명과 동일)
- 카테고리: 주 Medical, 보조 Utilities
- 연령 등급: 4+ (의료/치료 정보 "없음", 약물 언급 "없음")
- 개인정보 처리방침 URL: https://728haven-oss.github.io/pill-capture/privacy.html
- 앱 개인정보(App Privacy) 답변: "데이터를 수집하지 않음" (Data Not Collected)
- 저작권: © 2026 728haven
- 심사 정보(App Review Notes):
  > 로그인이 필요 없습니다. 카메라 권한을 허용한 뒤 하단 "실시간" 또는 "촬영"으로 알약을 찍으면 종류별 개수가 표시됩니다. 실제 알약이 없으면 우측 하단 새로고침(예시 이미지) 버튼으로 합성 예시 트레이를 불러와 동작을 확인할 수 있습니다. 앱은 어떤 데이터도 서버로 보내지 않습니다.
- 데모 계정: 필요 없음
- 수출 규정(암호화): 표준 HTTPS 외 암호화 없음 → ITSAppUsesNonExemptEncryption = NO

---

## 서명·업로드 (GitHub Actions 시크릿)

Play — 저장소 Settings → Secrets and variables → Actions:
| 시크릿 | 값 |
|---|---|
| ANDROID_KEYSTORE_BASE64 | 새 업로드 키스토어 upload.jks 의 base64 (앱마다 새 키 권장) |
| ANDROID_KEYSTORE_PASSWORD | 키스토어 비밀번호 |
| ANDROID_KEY_ALIAS | pillcapture |
| ANDROID_KEY_PASSWORD | 키 비밀번호(키스토어와 같으면 동일 값) |

키스토어 생성(Windows PowerShell, JDK 17):
```
keytool -genkeypair -v -keystore upload.jks -alias pillcapture -keyalg RSA -keysize 2048 -validity 10000
[Convert]::ToBase64String([IO.File]::ReadAllBytes("upload.jks")) | Set-Clipboard
```

App Store — 컨범 스토어에서 쓰던 값 재사용 가능: IOS_CERT_P12_BASE64, IOS_CERT_PASSWORD, APPLE_TEAM_ID, ASC_KEY_ID, ASC_ISSUER_ID, ASC_KEY_P8.
새로 필요한 것: IOS_PROFILE_BASE64 — developer.apple.com → Identifiers에서 App ID `kr.pillcapture.app` 등록 → Profiles에서 App Store 배포용 프로파일 생성 → .mobileprovision 을 base64.
App Store Connect → 나의 앱 → 신규 앱: 플랫폼 iOS, 이름 알약캡쳐, 기본 언어 한국어, 번들 ID kr.pillcapture.app, SKU pillcapture.

시크릿 등록 후: 저장소에 태그 `v1.0.0` 푸시 → Android Release(Play)가 서명 AAB, iOS(App Store)가 TestFlight 업로드까지 수행.
