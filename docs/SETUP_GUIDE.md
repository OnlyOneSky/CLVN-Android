# CLVN-Android Setup Guide

Complete setup guide for the CLVN-Android mobile test automation framework.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Setup](#project-setup)
- [Android Environment](#android-environment)
- [iOS Environment](#ios-environment)
- [Appium Setup](#appium-setup)
- [WireMock Setup](#wiremock-setup)
- [Sample App](#sample-app)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Test framework |
| Node.js | 18+ | Appium server, sample app |
| Docker | Latest | WireMock mock server |
| Git | Latest | Version control |
| Java (JDK) | 17 | Android builds |

### macOS (Homebrew)

```bash
brew install python@3.11 node openjdk@17 git docker
```

Set JAVA_HOME in your shell profile (`~/.zshrc`):

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"
```

---

## Project Setup

### 1. Clone the repo

```bash
git clone https://github.com/OnlyOneSky/CLVN-Android.git
cd CLVN-Android
```

### 2. Create virtual environment & install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
pip install -e .
```

### 3. IDE Setup (PyCharm)

Go to **Settings → Project → Python Interpreter → Add Interpreter → Existing** and select `.venv/bin/python`.

---

## Android Environment

### 1. Install Android SDK

```bash
brew install --cask android-commandlinetools
```

### 2. Set environment variables

Add to `~/.zshrc`:

```bash
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
```

Reload: `source ~/.zshrc`

### 3. Install SDK packages

```bash
# Accept licenses
yes | sdkmanager --licenses

# Install required packages
sdkmanager "platforms;android-36" \
           "build-tools;36.0.0" \
           "platform-tools" \
           "emulator" \
           "system-images;android-34;google_apis;arm64-v8a"
```

### 4. Create an emulator (AVD)

```bash
# Create a Pixel 7 emulator with Android 14
echo "no" | avdmanager create avd \
  -n "Pixel_7_API_34" \
  -k "system-images;android-34;google_apis;arm64-v8a" \
  -d "pixel_7"

# Verify
avdmanager list avd
```

### 5. Start the emulator

```bash
# With GUI
emulator -avd Pixel_7_API_34

# Headless (no window — useful for CI/servers)
emulator -avd Pixel_7_API_34 -no-window -no-audio -gpu swiftshader_indirect

# Verify it's running
adb devices -l
```

> **Tip:** The emulator takes 30-60 seconds to fully boot. Wait for `sys.boot_completed` = 1:
> ```bash
> adb shell getprop sys.boot_completed
> ```

### 6. Device info commands

```bash
# List connected devices
adb devices -l

# Get device model
adb -s emulator-5554 shell getprop ro.product.model

# Get Android version
adb -s emulator-5554 shell getprop ro.build.version.release

# Get manufacturer
adb -s emulator-5554 shell getprop ro.product.manufacturer
```

---

## iOS Environment

> Requires macOS with Xcode installed.

### 1. Install Xcode

Download from the App Store or [developer.apple.com](https://developer.apple.com/xcode/).

```bash
xcode-select --install
sudo xcodebuild -license accept
```

### 2. List available simulators

```bash
xcrun simctl list devices available
```

### 3. Boot a simulator

```bash
# Boot an iPhone 15 (find exact name from list above)
xcrun simctl boot "iPhone 15"

# Verify
xcrun simctl list devices booted
```

---

## Appium Setup

### 1. Install Appium 2.x

```bash
npm install -g appium
```

### 2. Install platform drivers

```bash
# Android
appium driver install uiautomator2

# iOS
appium driver install xcuitest
```

### 3. Verify installation

```bash
appium driver list --installed
```

### 4. Start Appium server

```bash
appium
# Default: http://127.0.0.1:4723
```

---

## WireMock Setup

WireMock is our API mock server. We package it as a custom Docker image with all stubs baked in — no volume mounts needed.

### Prerequisites

You need Docker installed. Options:

```bash
# Option A: Docker Desktop (GUI)
brew install --cask docker

# Option B: Colima + Docker CLI (lightweight, no GUI)
brew install colima docker
colima start
```

### Option 1: Pull the pre-built image (recommended)

Download `clvn-wiremock.tar` from the [GitHub Release](https://github.com/OnlyOneSky/CLVN-Android/releases):

```bash
# Load the image
docker load -i clvn-wiremock.tar

# Run it
docker run -d --name clvn-wiremock -p 8090:8080 clvn-wiremock:latest
```

### Option 2: Build from source

```bash
cd CLVN-Android
docker compose up -d
```

This builds the image from `wiremock/Dockerfile` and starts it.

### Verify it's running

```bash
# Check the container
docker ps | grep wiremock

# Check the stubs are loaded
curl http://localhost:8090/__admin/mappings
```

You should see the login stubs (success + failure) in the response.

### Stop / Restart

```bash
# Stop
docker stop clvn-wiremock

# Start again
docker start clvn-wiremock

# Or with docker-compose
docker compose down
docker compose up -d
```

### Managing stubs

**Pre-loaded stubs (baked into image):**
- `wiremock/mappings/` — Stub definitions (request matching → response)
- `wiremock/__files/` — Response body JSON files

**Adding new stubs:**
1. Add mapping JSON to `wiremock/mappings/`
2. Add response body to `wiremock/__files/` (if using `bodyFileName`)
3. Rebuild the image: `docker compose build`

**Programmatic stubs (in tests):**
Tests can also create/delete stubs at runtime via `WireMockClient`:

```python
# In a test
wiremock.create_stub({
    "request": {"method": "GET", "url": "/api/users"},
    "response": {"status": 200, "jsonBody": {"users": []}}
})
```

**Useful admin endpoints:**

| Endpoint | Purpose |
|----------|---------|
| `GET /__admin/mappings` | List all stubs |
| `POST /__admin/mappings` | Create a stub |
| `DELETE /__admin/mappings` | Delete all stubs |
| `POST /__admin/reset` | Reset stubs + request journal |
| `GET /__admin/requests` | View recorded requests |
| `POST /__admin/requests/count` | Count matching requests |

### Rebuilding the image after changes

When you update stubs and want to share the new image:

```bash
# Rebuild
docker compose build

# Export
docker save clvn-wiremock:latest -o clvn-wiremock.tar

# Share the .tar or create a new GitHub Release
```

---

## Sample App

The included React Native (Expo) sample app serves as the test target.

### Build Android APK

```bash
cd sample-app

# Install dependencies
npm install

# Generate native Android project WITH cleartext HTTP plugins
npx expo prebuild --clean

# Build release APK (bundles JS — works without Metro dev server)
cd android
./gradlew clean assembleRelease
```

APK location: `android/app/build/outputs/apk/release/app-release.apk`

> ⚠️ **Why release and not debug?** The debug APK requires a Metro dev server
> running to serve the JavaScript bundle. The release APK bundles everything
> so the app runs standalone — which is what we need for automated testing.

> 🔑 **Critical: `npx expo prebuild --clean` is required!**
> The `sample-app/android/` directory is gitignored because Expo generates it.
> The prebuild step applies our custom plugins that:
> - Enable cleartext HTTP traffic (needed for WireMock over `http://`)
> - Generate `network_security_config.xml` (React Native's OkHttp requires
>   this in release builds — the manifest attribute alone isn't sufficient)
>
> **If you skip this step, the app will get "Network request failed" errors
> because Android blocks cleartext HTTP in release builds by default.**

### Android Emulator Networking

The sample app uses `10.0.2.2` to reach the host machine's `localhost` from
inside the Android emulator. This is a built-in emulator alias — **no `adb
reverse` needed.**

| From | To reach host localhost | Method |
|------|------------------------|--------|
| Android emulator | `http://10.0.2.2:<port>` | Built-in alias (recommended) |
| Physical device | `http://<host-ip>:<port>` | Use `adb reverse tcp:<port> tcp:<port>` |

### Install on emulator/device

The test framework **auto-installs the APK** (and always reinstalls the latest
version when an APK path is configured). You can also install manually:

```bash
adb install -r sample-app/android/app/build/outputs/apk/release/app-release.apk
```

### Rebuilding after code changes

When you change the sample app's source code (e.g., `screens/LoginScreen.js`):

```bash
cd sample-app/android
./gradlew clean assembleRelease
```

The `clean` step is important — Gradle may cache the old JS bundle otherwise.
After rebuilding, the test framework will automatically reinstall the new APK.

### App Screens

| Screen | Elements (testID) | API Call |
|--------|------------------|----------|
| **Login** | `username_input`, `password_input`, `login_button`, `error_message` | `POST /api/login` |
| **Home** | `welcome_message`, `menu_button`, `logout_button` | — |

---

## Running Tests

### Start all services first

```bash
# Terminal 1: WireMock
docker compose up -d

# Terminal 2: Emulator (or connect a device)
emulator -avd Pixel_7_API_34 -no-window -no-audio -gpu swiftshader_indirect

# Terminal 3: Appium
appium

# Terminal 4: Run tests
source .venv/bin/activate
```

### Test commands

```bash
# Run all tests on all connected devices
pytest

# Android only
pytest --platform android

# iOS only
pytest --platform ios

# Smoke tests only
pytest -m smoke

# Regression suite
pytest -m regression

# Specific test file
pytest tests/test_login.py

# With verbose output
pytest -v --tb=long
```

### View Allure report

```bash
# Install Allure CLI (first time only)
brew install allure

# Generate and open report
allure serve allure-results
```

---

## Troubleshooting

### Emulator won't start

```bash
# Check if hardware acceleration is available
emulator -accel-check

# Try with different GPU mode
emulator -avd Pixel_7_API_34 -gpu host
```

### adb not found

Ensure `ANDROID_HOME` is set and `platform-tools` is in your PATH:

```bash
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
export PATH="$ANDROID_HOME/platform-tools:$PATH"
```

### Appium can't find device

```bash
# Kill and restart adb
adb kill-server
adb start-server
adb devices
```

### WireMock connection refused

```bash
# Check Docker is running
docker ps

# Restart WireMock
docker compose down && docker compose up -d
```

### App shows "Network request failed" / "Network error"

This usually means the Android release build is blocking cleartext HTTP. Fix:

1. **Did you run `npx expo prebuild --clean`?** This is the #1 cause. The Expo
   plugins that enable cleartext HTTP must be applied before building.

2. **Did you `clean` before building?** Run `./gradlew clean assembleRelease` —
   Gradle caches JS bundles aggressively.

3. **Is WireMock reachable from the emulator?** Open Chrome in the emulator and
   navigate to `http://10.0.2.2:8090/__admin/`. If this loads, networking is fine
   and the issue is in the app build.

4. **Full rebuild from scratch:**
   ```bash
   cd sample-app
   npx expo prebuild --clean
   cd android
   ./gradlew clean assembleRelease
   cd ../..
   adb uninstall com.clvn.sample
   pytest tests/ -v
   ```

### Tests fail with "No devices found"

The `DeviceManager` auto-discovers devices. Make sure:
1. Emulator is fully booted (`adb shell getprop sys.boot_completed` → `1`)
2. Or a physical device is connected and USB debugging is enabled
3. `adb devices` shows your device as `device` (not `unauthorized` or `offline`)
