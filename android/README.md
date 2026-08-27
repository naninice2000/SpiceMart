# 🌿 SpiceMart - Native Android Application

A high-performance, modern Android application for **SpiceMart** built with Kotlin, AndroidX, and Material 3.

---

## 📱 Features

- **Pure Native UX**: Edge-to-edge emerald system status bar matching `#059669`.
- **AndroidX Splash Screen**: Smooth brand launch transition with vector leaf logo.
- **Pull-to-Refresh**: Native `SwipeRefreshLayout` in emerald styling to refresh inventory.
- **Top Progress Bar**: Sleek `LinearProgressIndicator` tracking load state.
- **Offline Error Handling**: Native offline screen with retry button when disconnected.
- **Hardware Back Navigation**: Intercepts Android back gestures to traverse in-app browsing history.
- **External Intent Routing**: Automatically opens native apps for `tel:`, `mailto:`, and map links.
- **Google Sign-In & Cookie Persistence**: Configured for Google OAuth and cart persistence.

---

## 🛠️ Project Structure

```
android/
├── app/
│   ├── build.gradle.kts           # Application configuration & dependencies
│   ├── proguard-rules.pro         # Proguard optimization rules
│   └── src/main/
│       ├── AndroidManifest.xml    # Permissions, activities & deep link filters
│       ├── java/com/spicemart/app/
│       │   ├── MainActivity.kt    # Core controller & settings
│       │   ├── SpiceMartWebViewClient.kt # URL routing & error handling
│       │   ├── SpiceMartWebChromeClient.kt # Progress & alerts
│       │   └── NetworkUtils.kt    # Real-time network detector
│       └── res/                   # Drawables, layouts, colors, strings, themes
├── build.gradle.kts               # Root build script
├── settings.gradle.kts            # Module settings
└── gradle/wrapper/                # Gradle 8.7 wrapper
```

---

## 🚀 How to Open and Run in Android Studio

1. Open **Android Studio** (Hedgehog / Iguana / Jellyfish / Koala or newer).
2. Select **Open** and choose the `android/` folder inside `SpiceMart`.
3. Wait for Gradle Sync to complete.
4. Connect an Android device (via USB with USB Debugging enabled) or start an Android Emulator.
5. Click **Run** (▶️) or press `Shift + F10`.

---

## 📦 How to Build Release APK / AAB

To build a standalone APK for testing or distribution:

```bash
cd android
./gradlew assembleRelease
```
The generated APK will be located at:
`android/app/build/outputs/apk/release/app-release.apk`

To build an Android App Bundle (AAB) for Google Play:
```bash
./gradlew bundleRelease
```
