# UPI Shield AI — Android starter project

A mobile-first Kivy app for a UPI safety / scam-awareness project.

## What's included
- Mobile dashboard with a dark, premium shield-themed UI
- Message scam indicator (transparent rule-based checks)
- UPI URI inspector (paste a decoded `upi://pay` URI)
- UPI safety learning cards
- Interactive safety quiz
- No payment functionality, no bank login, and no collection of OTPs, PINs or credentials

## Important notes
This is an educational prototype, not a bank product and not a certified AI fraud detector.
The message scanner uses simple keyword/rule scoring. A low score does not prove a message is safe.
The QR page currently inspects a pasted decoded UPI URI; camera-based QR decoding is not included in this starter build.

## Run on desktop for preview
Python 3.10–3.12 recommended:
```bash
python -m pip install kivy
python main.py
```

## Build an Android APK
Buildozer is best run on Linux (Ubuntu) or WSL2 Ubuntu, not directly on standard Windows.
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
  autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
  libtinfo6 cmake libffi-dev libssl-dev
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install buildozer cython==0.29.36
buildozer android debug
```
The first build downloads Android SDK/NDK components and can take a while. The APK is normally created under `bin/`.
Install on a connected Android phone (USB debugging enabled):
```bash
buildozer android debug deploy run
```
Or copy the generated APK from `bin/` to your phone and install it after allowing installs from that source.

## Build configuration
The included `buildozer.spec` replaces the uploaded desktop-oriented configuration. Tkinter / CustomTkinter are not Android UI frameworks, so they were removed. Kivy provides the mobile interface.

## Safety
Never enter or share a real UPI PIN, OTP, password, bank login, or card details in this demo. Verify payee name and amount in your official UPI app. In India, report cyber financial fraud promptly via 1930 or https://cybercrime.gov.in/.
