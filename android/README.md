# Android native alpha launcher

This is a real Kotlin Android **app project** which embeds the responsive SuperScreen browser receiver. It saves the host address and provides a route to phone Wi-Fi/hotspot settings. **The image decoder is still the web viewer's JPEG canvas.** It is not a MediaCodec app, does not create a second monitor and does not auto-activate the Android hotspot.

## Build

Open `android/` in Android Studio with JDK 17 and compile SDK 35 installed. Sync Gradle. Use **Build → Build APK(s)**. This project pins Android Gradle Plugin 8.6.1 and Kotlin 2.0.21. It does not currently contain a Gradle wrapper binary; an IDE-managed Gradle distribution or system Gradle 8.10.2 is required. No hardware build has yet been verified.

## Connect

1. Turn on the Android phone's hotspot.
2. Connect the Windows laptop to the hotspot.
3. Start the SuperScreen Windows host using `python -m superscreen`.
4. Enter the laptop's Wi-Fi IPv4 address (printed in PowerShell) in the Android app.
5. Enter the six-digit pairing code in the embedded viewer.

Saved addresses reconnect through the embedded web interface when the user opens it again. IP changes may require manually updating the saved address.

## Security

The manifest enables unencrypted local HTTP only for this experimental private-hotspot phase. This app is not suitable for release to end users until authenticated encryption, device verification, certificate pinning and proper input permissions are added.
