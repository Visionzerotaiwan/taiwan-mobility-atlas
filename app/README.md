# 還路於民 — Capacitor store app (iOS + Android)

Native shell that wraps the live atlas (`https://yunching0513.github.io/taiwan-mobility-atlas/`)
into App Store / Play Store apps using **Capacitor 7**. The web app is already a PWA;
this project only adds the native wrappers, icons, splash screens, and store plumbing.

> **Everything here runs on _your_ Mac** — building and submitting needs Xcode / Android
> Studio and paid developer accounts, which can't run in an automated environment.

---

## 0. One-command bootstrap

```bash
cd app
bash setup.sh
```

`setup.sh` runs `npm install`, generates the native icons/splash from `app/assets/`,
adds the **iOS** platform (your Mac has Xcode + CocoaPods), and **skips Android** until
Android Studio is installed. Then:

```bash
npx cap open ios       # opens Xcode
npx cap open android   # opens Android Studio (after you install it)
```

Confirm your Capacitor version first — `npx cap --version`. This scaffold pins **v7**.
(Capacitor **8** exists and moves iOS to Swift Package Manager by default with a newer
toolchain; if `npx cap --version` shows 8, follow the v8 icon/SPM notes in the Capacitor docs.)

---

## Your machine, right now
- ✅ **iOS-ready:** Node 24, Xcode 26.5, CocoaPods 1.16 detected.
- ⚠️ **Android needs setup:** install **[Android Studio](https://developer.android.com/studio)**
  (bundles JDK 21 + the Android SDK), then re-run `bash setup.sh` (or
  `npx cap add android && npx cap sync android && npm run assets`).
- ⚠️ **CocoaPods locale bug:** `pod install` dies with *"Unicode Normalization … ASCII-8BIT"*
  if the shell has no UTF-8 locale. `setup.sh` exports `LANG=en_US.UTF-8` to avoid it; if you
  run `pod install` by hand, prefix it the same way.

---

## App identity
| Field | Value | Notes |
|---|---|---|
| `appId` | `tw.visionzero.atlas` | Becomes iOS **Bundle ID** + Android **applicationId**. Must match your store registration. |
| `appName` | `還路於民` | Native display name (rename in `capacitor.config.json`). |
| Loads | live site via `server.url` | See **Config & the 4.2 warning** below. |

---

## iOS — build & submit
Prereqs: **Xcode 16+**, **Node 20+**, **CocoaPods**, **Apple Developer Program (US$99/yr)**.

1. `bash setup.sh` (or `npx cap add ios && npx cap sync ios`).
2. `npx cap open ios` → in Xcode, **App target ▸ Signing & Capabilities**: set **Bundle Identifier** = `tw.visionzero.atlas`, tick **Automatically manage signing**, pick your **Team**.
3. Icons/splash: sources live in `app/assets/` (`icon-only.png` 1024², `splash.png` / `splash-dark.png` 2732²). Regenerate with `npm run assets` then `npx cap sync ios`.
4. **Privacy manifest (required by Apple):** Capacitor does **not** create an app-level `PrivacyInfo.xcprivacy`. In Xcode → **File ▸ New ▸ File ▸ App Privacy File**, target **App**, and declare tracking = false plus any required-reason API codes for plugins you add later (this scaffold only uses SplashScreen + StatusBar). 
5. Set **Version** + **Build** (App target ▸ General), choose **Any iOS Device (arm64)**, then **Product ▸ Archive ▸ Distribute App ▸ App Store Connect**. Build lands in **TestFlight**; fill metadata + privacy nutrition label in App Store Connect and **Submit for Review**.

## Android — build & submit
Prereqs: **Android Studio** (bundles JDK 21 + SDK), **Google Play Console (US$25 one-time)**.

1. Install Android Studio, then `npx cap add android && npx cap sync android && npm run assets`.
2. `npx cap open android`. `applicationId` is already `tw.visionzero.atlas`.
3. **Target API 35 is mandatory** for new apps / updates (Google Play, since Aug 2025) — Capacitor 7 already targets 35.
4. Create an upload keystore once:
   ```bash
   keytool -genkey -v -keystore vzt-upload.jks -alias vzt -keyalg RSA -keysize 2048 -validity 10000
   ```
   (Keep it safe and **out of git** — `*.jks`/`*.keystore` are already ignored.)
5. Android Studio → **Build ▸ Generate Signed App Bundle** → select the keystore → produces `app-release.aab`. Upload to **Play Console**; enrol in **Play App Signing**; complete the **Data safety** form (you must declare data handling because the app loads a site you control), then roll out.

---

## Config & the 4.2 warning (read this)
`capacitor.config.json` points the WebView at the **live site** (`server.url`). This keeps the
app tiny and always current, and external links (petition, visionzero.tw) open in the system
browser via `allowNavigation`. HTTPS-only, so no iOS ATS exception and Android cleartext stays off.

**Two caveats you should weigh before submitting:**
1. Capacitor's docs call `server.url` *"not intended for use in production"* — it works and is
   widely used for remote wrappers, but **you own uptime** and there's **no offline**.
2. **App Store Guideline 4.2 ("minimum functionality")** frequently rejects apps that are just a
   web page in a WebView. Mitigations, strongest first:
   - **Bundle the site for offline first-launch** (see below) — the single biggest fix.
   - Add genuine native features via plugins (Push, Geolocation for「我家附近」, native Share, Haptics).
   - Make it feel native (no browser chrome — already the case).

### Offline / bundled mode (recommended for App Store)
Instead of `server.url`, ship the web assets inside the app:
1. Copy the site into `app/www/` (exclude the huge datasets to keep the binary small):
   ```bash
   rsync -a --delete --exclude 'app' --exclude '.git' \
     --exclude 'data/poles' --exclude 'data/sidewalks26' \
     ../ ./www/
   ```
2. Remove (or comment out) the `server` block in `capacitor.config.json`.
3. `npx cap sync`. The app now launches offline; the poles / sidewalk-segment layers still fetch
   from the live site when online.

---

## Files
```
app/
├─ capacitor.config.json   # appId, appName, server.url, splash/status-bar
├─ package.json            # Capacitor 7 deps + scripts
├─ setup.sh                # one-command bootstrap (iOS now, Android after Android Studio)
├─ www/index.html          # local fallback shown offline / in bundled mode
├─ assets/                 # icon-only / icon-foreground / icon-background / splash / splash-dark
├─ .gitignore              # node_modules, ios/, android/, keystores
└─ ios/ · android/         # generated by `cap add …` (git-ignored until you customise them)
```
After you customise `ios/` or `android/` (signing, Info.plist, etc.), remove them from
`.gitignore` and commit so your changes are tracked.
