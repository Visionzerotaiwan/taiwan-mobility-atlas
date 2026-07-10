#!/usr/bin/env bash
# One-shot bootstrap for the Capacitor store scaffold (iOS + Android).
# Run from the app/ folder:  bash setup.sh
set -e
cd "$(dirname "$0")"

# CocoaPods needs a UTF-8 locale, or `pod install` dies with
# "Unicode Normalization not appropriate for ASCII-8BIT". Force one.
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

echo "▸ Installing npm dependencies…"
npm install

echo "▸ Generating app icons & splash screens from app/assets/…"
npx capacitor-assets generate \
  --iconBackgroundColor '#E5E670' --iconBackgroundColorDark '#141414' \
  --splashBackgroundColor '#E5E670' --splashBackgroundColorDark '#141414' || \
  echo "  (asset generation will run again after a platform is added)"

# iOS — needs Xcode + CocoaPods (both detected on this Mac).
if command -v xcodebuild >/dev/null 2>&1; then
  echo "▸ Adding iOS platform…"
  [ -d ios ] || npx cap add ios
  npx cap sync ios
  npx capacitor-assets generate --ios \
    --iconBackgroundColor '#E5E670' --splashBackgroundColor '#E5E670' --splashBackgroundColorDark '#141414' || true
  echo "  ✓ iOS ready →  npx cap open ios"
else
  echo "▸ Skipping iOS (Xcode not found)."
fi

# Android — needs Android Studio (JDK + Android SDK).
if command -v adb >/dev/null 2>&1 || [ -n "${ANDROID_HOME:-}" ]; then
  echo "▸ Adding Android platform…"
  [ -d android ] || npx cap add android
  npx cap sync android
  npx capacitor-assets generate --android \
    --iconBackgroundColor '#E5E670' --iconBackgroundColorDark '#141414' \
    --splashBackgroundColor '#E5E670' --splashBackgroundColorDark '#141414' || true
  echo "  ✓ Android ready →  npx cap open android"
else
  echo "▸ Skipping Android — install Android Studio first (bundles JDK + SDK), then re-run:"
  echo "     npx cap add android && npx cap sync android && npm run assets"
fi

echo "▸ Done. Open the native IDEs with:  npx cap open ios   |   npx cap open android"
