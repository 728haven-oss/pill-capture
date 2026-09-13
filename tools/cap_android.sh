#!/usr/bin/env bash
# Capacitor 안드로이드 프로젝트 생성 + 앱 이름/아이콘/카메라 권한 적용 (CI용)
set -euo pipefail
npm install
npx cap add android
npx cap sync android
# Play 요구: targetSdk 36 이상 (2026) → SDK 36 + AGP 8.9 / Gradle 8.11
sed -i 's/compileSdkVersion = [0-9]*/compileSdkVersion = 36/; s/targetSdkVersion = [0-9]*/targetSdkVersion = 36/' android/variables.gradle
sed -i "s/com.android.tools.build:gradle:[0-9.]*/com.android.tools.build:gradle:8.9.1/" android/build.gradle
sed -i 's|gradle-[0-9.]*-all.zip|gradle-8.11.1-all.zip|' android/gradle/wrapper/gradle-wrapper.properties
grep -n "SdkVersion" android/variables.gradle; grep -n "tools.build:gradle" android/build.gradle; grep -n distributionUrl android/gradle/wrapper/gradle-wrapper.properties
S=android/app/src/main/res
sed -i 's|<string name="app_name">.*</string>|<string name="app_name">알약캡쳐</string>|;s|<string name="title_activity_main">.*</string>|<string name="title_activity_main">알약캡쳐</string>|' $S/values/strings.xml
# 카메라 권한: <input type=file capture> 와 getUserMedia 가 WebView에서 카메라를 열 수 있도록 (Capacitor가 런타임 권한 요청 처리)
M=android/app/src/main/AndroidManifest.xml
grep -q 'android.permission.CAMERA' $M || sed -i 's|<uses-permission android:name="android.permission.INTERNET" />|<uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.CAMERA" />\n    <uses-feature android:name="android.hardware.camera" android:required="false" />|' $M
grep -n "CAMERA" $M
# 아이콘
for d in mdpi hdpi xhdpi xxhdpi xxxhdpi; do
  mkdir -p $S/mipmap-$d
  cp assets/icons/icon-512.png $S/mipmap-$d/ic_launcher.png
  cp assets/icons/icon-512.png $S/mipmap-$d/ic_launcher_round.png
  cp assets/icons/icon-foreground.png $S/mipmap-$d/ic_launcher_foreground.png
done
rm -rf $S/mipmap-anydpi-v26
# 스플래시
for d in drawable drawable-port-mdpi drawable-port-hdpi drawable-port-xhdpi drawable-port-xxhdpi drawable-port-xxxhdpi drawable-land-mdpi drawable-land-hdpi drawable-land-xhdpi drawable-land-xxhdpi drawable-land-xxxhdpi; do
  [ -d $S/$d ] && cp assets/icons/splash-2732.png $S/$d/splash.png || true
done
echo "cap android ready"
