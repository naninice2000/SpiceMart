# 🍏 SpiceMart - Native iOS Application

A high-performance, modern iOS application for **SpiceMart** built with Swift, SwiftUI, and WebKit (`WKWebView`). It delivers a pure native iOS experience with emerald theme styling, gesture navigation, native pull-to-refresh, and offline handling.

---

## 📱 Key Native Features

- **Edge-to-Edge Emerald System Styling**: Status bar and safe area seamlessly match the `#059669` store theme.
- **Native Pull-to-Refresh (`UIRefreshControl`)**: Custom emerald spinner to refresh the store inventory.
- **Swipe-to-Go-Back Gestures**: Native interactive edge-swipe navigation (`allowsBackForwardNavigationGestures`).
- **Top Linear Progress Indicator**: Thin, sleek progress bar tracking real-time loading progress.
- **Real-Time Network Monitoring (`NWPathMonitor`)**: Native SwiftUI offline error screen with an instant **"Retry Connection"** button.
- **System Intent Handling**: Direct routing for phone calls (`tel:`), emails (`mailto:`), SMS (`sms:`), and Apple Maps (`maps:`).
- **Google OAuth & Cart Storage**: Clean Mobile Safari User-Agent and `WKWebsiteDataStore` for Google Sign-In and saved carts.

---

## 🛠️ Project Structure

```
ios/
├── SpiceMart.xcodeproj/
│   └── project.pbxproj            # Xcode project configuration
├── SpiceMart/
│   ├── App/
│   │   └── SpiceMartApp.swift     # SwiftUI @main entry point & lifecycle
│   ├── Views/
│   │   ├── ContentView.swift      # Main container coordinating WebView & offline states
│   │   ├── WebViewContainer.swift # UIViewRepresentable wrapping WKWebView & UIRefreshControl
│   │   └── OfflineView.swift      # Native SwiftUI offline error screen
│   ├── Services/
│   │   ├── NetworkMonitor.swift   # Real-time NWPathMonitor network listener
│   │   └── WebViewModel.swift     # ObservableObject managing progress, URL states & errors
│   ├── Config/
│   │   └── AppConfig.swift        # Central configuration (Store URL, brand colors)
│   └── Resources/
│       ├── Assets.xcassets/       # AppIcon, AccentColor (#059669)
│       ├── Info.plist             # App Transport Security & orientations
│       └── LaunchScreen.storyboard# Storyboard launch screen with emerald background
└── README.md                      # Guide for building, running on iOS Simulator and physical iPhone
```

---

## 📋 Prerequisites

- **Mac**: macOS Sonoma / Sequoia or newer
- **Xcode**: Xcode 15.0 or newer (Download free from the [Mac App Store](https://apps.apple.com/app/xcode/id497799835))
- **iOS Device / Simulator**: iOS 15.0 or newer

---

## 🚀 How to Run in iOS Simulator

1. Open **Xcode**.
2. Click **Open Existing Project** and choose the `ios/SpiceMart.xcodeproj` file.
3. In the top toolbar, select any iPhone Simulator (e.g. **iPhone 15 Pro** / **iPhone 16**).
4. Click the **Run (▶️)** button (or press `⌘ + R`).
5. The iOS Simulator will boot and launch **SpiceMart**!

---

## 📲 How to Install onto Your Physical iPhone

You can install SpiceMart directly onto your iPhone for free without a paid Apple Developer account:

1. **Connect Your iPhone**:
   - Plug your iPhone into your Mac using a Lightning / USB-C cable.
   - Unlock your iPhone and tap **"Trust This Computer"** if prompted.
2. **Open the Project in Xcode**:
   - Open `ios/SpiceMart.xcodeproj`.
3. **Configure Code Signing (Free Apple ID)**:
   - Click on the root **SpiceMart** project in the left sidebar.
   - Select the **SpiceMart** target under *Targets*.
   - Go to the **Signing & Capabilities** tab.
   - Check **"Automatically manage signing"**.
   - Under **Team**, select your Personal Apple ID (click *Add Account...* if not logged in).
   - In **Bundle Identifier**, change `com.spicemart.ios` to a unique identifier if needed (e.g., `com.yourname.spicemart`).
4. **Select Your Device & Run**:
   - In the top device dropdown, select your connected iPhone.
   - Press **Run (▶️)** (or `⌘ + R`).
5. **Trust the Certificate on Your iPhone (First Time Only)**:
   - On your iPhone, open **Settings** > **General** > **VPN & Device Management**.
   - Under *Developer App*, tap your Apple ID and tap **"Trust"**.
   - Open **SpiceMart** from your iPhone home screen!

---

## ⚙️ Configuration & Customization

| Item | File Location | Description |
|---|---|---|
| **Store URL** | `SpiceMart/Config/AppConfig.swift` | Change `storeURL = URL(string: "...")` |
| **Brand Colors** | `SpiceMart/Config/AppConfig.swift` | Change `emerald600` or brand color palette |
| **App Display Name** | `SpiceMart/Resources/Info.plist` | Change `<string>SpiceMart</string>` under `CFBundleDisplayName` |
| **Bundle Identifier** | `SpiceMart.xcodeproj` | Change `PRODUCT_BUNDLE_IDENTIFIER` |
| **App Icons** | `SpiceMart/Resources/Assets.xcassets/AppIcon.appiconset/` | Add 1024x1024 PNG icon |

---

## 📄 License

Copyright © 2026 SpiceMart. All rights reserved.
