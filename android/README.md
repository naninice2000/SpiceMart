# 🌿 SpiceMart - Native Android Application

A high-performance, modern Android application for **SpiceMart** built with Kotlin, AndroidX, and Material 3. It wraps `https://naninice2000.github.io/SpiceMart/` into a pure native mobile experience with native hardware navigation, offline handling, emerald theme styling, and gesture controls.

---

## 📱 Key Native Features

- **Edge-to-Edge Emerald System Bars**: Status bar and navigation bar seamlessly blend with the `#059669` store theme.
- **AndroidX Core Splash Screen**: Smooth launch animation with vector brand leaf logo.
- **Native Pull-to-Refresh**: `SwipeRefreshLayout` with custom emerald loading spinner to reload catalog inventory.
- **Top Linear Progress Indicator**: Thin, sleek progress bar tracking page loading state.
- **Offline Error Handling**: Material 3 offline screen with an instant **"Retry Connection"** button when network is lost.
- **Hardware Back Button Handling**: Intercepts Android back gestures (`OnBackPressedCallback`) to navigate web history before exiting.
- **External Intent Routing**: Automatically opens native apps for phone calls (`tel:`), emails (`mailto:`), SMS (`sms:`), and Google Maps (`geo:`).
- **Google OAuth & Cart Storage**: Mobile Chrome User-Agent configuration, cookie manager, and DOM storage persistence for smooth Google Sign-In and saved carts.

---

## 🛠️ Project Structure

```
android/
├── app/
│   ├── build.gradle.kts           # Application configuration, SDK 34, dependencies
│   ├── proguard-rules.pro         # Proguard / R8 optimization rules
│   └── src/main/
│       ├── AndroidManifest.xml    # Permissions, hardware acceleration & deep links
│       ├── java/com/spicemart/app/
│       │   ├── MainActivity.kt    # Core WebView controller & lifecycle
│       │   ├── SpiceMartWebViewClient.kt # In-app routing, intent delegation & errors
│       │   ├── SpiceMartWebChromeClient.kt # Progress indicator & JS dialogs
│       │   └── NetworkUtils.kt    # Real-time network detector
│       └── res/                   # Drawables, layouts, colors, strings, themes
├── build.gradle.kts               # Root build script
├── settings.gradle.kts            # Module repository resolution
├── local.properties               # Android SDK path configuration
└── gradle/wrapper/                # Gradle 8.7 wrapper
```

---

## 📋 Prerequisites

- **Java Development Kit (JDK)**: OpenJDK 17 or higher
- **Android SDK**: Platform API 34 (`platforms;android-34`), Build Tools (`build-tools;34.0.0`), Platform Tools (`adb`)
- **(Optional)**: **Android Studio** (Hedgehog, Iguana, Jellyfish, Koala or newer)

---

## 🔨 Step-by-Step: How to Build & Install Debug Version on Android

### Step 1: Prepare Your Environment
Ensure Java 17 and Android tools are in your environment:
```bash
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$HOME/Library/Android/sdk/platform-tools:$PATH"
```

---

### Step 2: Set Up Your Android Phone (Samsung / Pixel / Motorola / OnePlus)
1. **Enable Developer Options**:
   - Open **Settings** > **About phone** > **Software information**.
   - Tap **Build number** 7 times quickly until the message *"Developer mode has been enabled"* appears.
2. **Enable USB Debugging**:
   - Go back to **Settings** > **Developer options**.
   - Turn ON **USB debugging**.
3. **Connect & Authorize USB Debugging**:
   - Connect your phone to your computer using a USB cable.
   - Unlock your phone screen.
   - Look for the popup prompt: **"Allow USB debugging?"**
   - Check **☑️ Always allow from this computer** and tap **Allow**.

4. **Verify Phone is Connected**:
   Run in your terminal:
   ```bash
   adb devices
   ```
   **Expected Output:**
   ```
   List of devices attached
   RZCX51YAZGL    device
   ```
   *(If it says `unauthorized`, unlock your phone screen and accept the prompt, or toggle USB debugging OFF and ON again).*

---

### Step 3: Build the Debug APK
Navigate to the `android/` directory and compile the debug APK using the Gradle wrapper:

```bash
cd /Users/venkata/workspace/PersonalBranding/SpiceMart/android
./gradlew assembleDebug
```

> 💡 **Build Output Location:**  
> `android/app/build/outputs/apk/debug/app-debug.apk`

---

### Step 4: Install the Debug APK onto Your Phone
With your phone connected via USB:

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

**Terminal Output upon success:**
```
Performing Streamed Install
Success
```

---

### Step 5: Launch the App on Your Phone
You can open **SpiceMart** directly from your phone's home screen/app drawer, or launch it immediately from the terminal:

```bash
adb shell am start -n com.spicemart.app.debug/com.spicemart.app.MainActivity
```

---

## 🚀 Alternative: Running via Android Studio

1. Open **Android Studio**.
2. Select **Open** and choose `/Users/venkata/workspace/PersonalBranding/SpiceMart/android`.
3. Allow Gradle to finish syncing dependencies.
4. Select your connected phone from the top device dropdown.
5. Click the green **Run (▶️)** button (or press `Shift + F10` / `Control + R`).

---

## 📦 Building Release APK & Google Play Bundle

### 1. Build Standalone Release APK:
```bash
cd android
./gradlew assembleRelease
```
Output: `app/build/outputs/apk/release/app-release.apk`

### 2. Build Android App Bundle (AAB) for Google Play:
```bash
cd android
./gradlew bundleRelease
```
Output: `app/build/outputs/bundle/release/app-release.aab`

---

## ⚙️ Configuration & Customization

| Item | File Location | Description |
|---|---|---|
| **Store URL** | `app/src/main/res/values/strings.xml` | Change `<string name="app_url">...</string>` |
| **App Name** | `app/src/main/res/values/strings.xml` | Change `<string name="app_name">...</string>` |
| **Brand Colors** | `app/src/main/res/values/colors.xml` | Update `emerald_600` (`#059669`) or theme palette |
| **Package ID** | `app/build.gradle.kts` | Change `applicationId = "com.spicemart.app"` |
| **App Icons** | `app/src/main/res/drawable/` & `mipmap/` | Replace `ic_launcher_foreground.xml` / `splash_icon.xml` |

---

## 📄 License

Copyright © 2026 SpiceMart. All rights reserved.
