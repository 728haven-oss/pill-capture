# 알약캡쳐 1.1.0 — 로그인 + 가입 후 2개월 무료 설정 가이드

앱 코드는 이미 준비돼 있습니다. 아래 계정·키만 만들면 켜집니다.
켜는 방법: `config/auth.json` 의 `enabled` 를 `true` 로, `supabaseUrl`/`supabaseAnonKey` 를 채우고 커밋 → 태그 푸시.
(키를 저장소에 넣기 싫으면 GitHub Secrets `SUPABASE_URL`, `SUPABASE_ANON_KEY` 로 넣으면 빌드 때 주입됩니다.)

## 1. Supabase (서버·무료 요금제)
1. https://supabase.com 가입 → New project (리전: Northeast Asia (Seoul))
2. SQL Editor 에 `supabase/schema.sql` 붙여넣고 실행 → profiles 테이블·가입 트리거 생성
3. Project Settings → API 에서 **Project URL** 과 **anon public key** 복사
4. Authentication → URL Configuration → Redirect URLs 에 아래 두 개 추가
   - `https://728haven-oss.github.io/pill-capture/index.html` (웹/PWA)
   - `kr.pillcapture.app://auth` (앱)

## 2. 카카오
1. https://developers.kakao.com → 내 애플리케이션 → 애플리케이션 추가
2. 제품 설정 → 카카오 로그인 → 활성화 ON
3. Redirect URI 에 `https://<프로젝트>.supabase.co/auth/v1/callback`
4. 동의 항목: 닉네임(필수), 이메일(선택)
5. 앱 키의 **REST API 키** + 보안 → **Client Secret** 발급
6. Supabase → Authentication → Providers → Kakao 에 위 두 값 입력

## 3. 구글
1. Google Cloud Console(`pill-capture` 프로젝트) → API 및 서비스 → 사용자 인증 정보
2. OAuth 클라이언트 ID(웹) 생성 → 승인된 리디렉션 URI `https://<프로젝트>.supabase.co/auth/v1/callback`
3. 클라이언트 ID/시크릿 → Supabase Providers → Google

## 4. Apple (아이폰 심사 필수)
1. developer.apple.com → Identifiers → Services ID 생성(예: `kr.pillcapture.signin`)
2. Sign in with Apple 활성화 → Return URL `https://<프로젝트>.supabase.co/auth/v1/callback`
3. Keys → Sign in with Apple 용 키(.p8) 발급 → Key ID, Team ID(Z68GT8B24X), .p8 내용
4. Supabase Providers → Apple 에 Services ID / Team ID / Key ID / .p8 입력

## 5. 네이버 (선택, 나중에 해도 됨)
Supabase 기본 제공 목록에 네이버가 없어서 Edge Function 한 개가 필요합니다.
1. https://developers.naver.com → 애플리케이션 등록 → 네이버 로그인 사용, Callback URL 은 Edge Function 주소
2. Edge Function 에서 네이버 토큰을 검증하고 Supabase Admin API 로 사용자 생성/로그인
3. 준비되면 `config/auth.json` 의 `providers.naver` 를 `true` 로

## 동작 방식
- 첫 실행 시 로그인 화면이 뜨고, 로그인하면 `profiles.trial_started_at` 이 서버에 기록됩니다.
- 가입일로부터 `trialDays`(기본 60일) 동안은 모든 기능이 열립니다(앱 내부적으로 Pro 와 동일).
- 60일이 지나면 기존 구독 로직이 그대로 작동합니다. 단 **결제는 현재 꺼져 있으므로**(`config/billing.json`)
  구독을 팔기 전에 `bash tools/enable_billing.sh` 로 결제를 다시 켜야 합니다.
- 계정에 저장되는 정보: 로그인 식별자(이메일/닉네임)와 가입일뿐입니다. 사진은 서버로 전송되지 않습니다.

## 앱 빌드 시 추가로 필요한 네이티브 플러그인
로그인 창을 시스템 브라우저로 열고 앱으로 돌아오기 위해 아래 두 개가 필요합니다(켜때 같이 추가).
```
npm i @capacitor/browser @capacitor/app
```
그리고 iOS `Info.plist` / Android `AndroidManifest.xml` 에 커스텀 스킴 `kr.pillcapture.app` 등록이 필요합니다(CI 스크립트에 추가 예정).
