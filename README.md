# 🚗 Virginia DMV Learner's Permit Exam Simulator

A 100% local, zero-dependency web application and study tool designed to simulate the computerized Virginia DMV Knowledge Exam and prepare learners to pass on their first attempt.

Optimized specifically for **desktop browsers** and **mobile devices / iPads** connected to your local home network.

---

## 🌟 Key Features

### 1. 🏛️ Official Virginia DMV Exam Simulation
Faithfully reproduces the official two-part computer exam administered at Virginia DMV Customer Service Centers:
- **Part 1 (Traffic Signs)**:
  - 10 randomly selected road signs questions.
  - **100% Passing Rule**: You **must** answer all 10 questions correctly. Missing even one question immediately discontinues the exam and provides diagnostic review with the official manual rule.
- **Part 2 (General Knowledge)**:
  - 30 randomly selected questions on Virginia laws, right-of-way, following distance, and penalties.
  - **80% Passing Rule**: Requires 24 correct answers out of 30.
  - **Authentic Early Termination**: As soon as you reach 24 correct, you receive the official Passing Screen; if you reach 7 incorrect, the test discontinues early.

### 2. 📱 Seamless iPad & Tablet Local Connection
- Runs entirely on your local machine—no internet connection required.
- Automatically discovers your Mac's local network IP address (`192.168.x.x` or `10.0.x.x`).
- Built-in dynamic **QR Code** right on screen: simply open the iPad Camera, point it at your screen, and tap to launch in iPad Safari!
- iPad touch targets (minimum 48-60px), smooth touch interactions, and Apple standalone web app mode (**"Add to Home Screen"** for full-screen kiosk feel).
- **Service Worker PWA** offline caching: once loaded, the app keeps running on your iPad even if your computer temporarily goes to sleep.

### 3. 📝 Practice & Study Modes
- **Practice Mode**: Answer all 40 questions with immediate feedback, detailed explanations, and citations to the *Virginia Driver's Manual*.
- **Sign Flashcards & Visual Catalog**: 3D interactive flip cards for 38+ Virginia road signs (Regulatory, Warning, School, Work Zone, Railroad). Filter by category and mark signs as "Mastered".
- **Topic-Specific Quizzes**: Focused drilling on high-stakes topics:
  - The 2-, 3-, and 4-Second Following Distance Rule
  - Statutory Speed Limits (25, 35, 55 MPH) & Reckless Driving (85+ MPH)
  - Virginia DUI & Zero Tolerance (0.02% under 21, 0.08% adult) & Implied Consent
  - School Bus Stopping Rules & Move Over Law
  - Parking Buffer Distances (15 ft hydrant, 20 ft crosswalk, 50 ft railroad)
  - Teen Curfew (Midnight - 4 AM) & Cell Phone Bans
- **Missed Questions Bank**: Automatically logs questions you answered incorrectly so you can drill them until 100% mastery.
- **Fast-Recall Cheat Sheet**: Consolidated reference tables for quick memorization before your exam appointment.
- **🔊 DMV Audio Test Simulation**: Uses local Web Speech API to read questions and answer choices aloud with a single tap.
- **🎨 3 UI Themes**: Modern Responsive, Dark Mode, and Retro **Virginia DMV Touch Terminal Kiosk**.

---

## 🚀 How to Run

### Quick Start (One Command)
In your terminal, navigate to the folder and run:
```bash
./run.sh
```
Or directly with Python 3:
```bash
python3 server.py
```

The terminal will print:
```
====================================================================
 🚗 VIRGINIA DMV LEARNER'S PERMIT EXAM SIMULATOR (100% LOCAL)
====================================================================
 Local Mac Access:               👉 http://localhost:8080/
 iPad / iPhone / Tablet Access:  👉 http://10.0.0.12:8080/
====================================================================
 Scan this QR Code with your iPad Camera to open instantly:
--------------------------------------------------------------------
  [ASCII QR CODE]
--------------------------------------------------------------------
```

---

## 📱 Connecting from your iPad or iPhone

1. Make sure your iPad is on the **same Wi-Fi network** as your Mac.
2. Open the **Camera app** on your iPad.
3. Aim the camera at the QR code displayed on your computer screen (or in the "Connect iPad" button inside the web app).
4. Tap the yellow **"Open in Safari"** prompt.
5. *(Optional Pro-Tip)*: In iPad Safari, tap the **Share** button (box with arrow) and select **"Add to Home Screen"**. This installs the app icon on your iPad and runs it full-screen without Safari browser bars, replicating the actual touch kiosk terminal at the DMV!

---

## 📁 Project Architecture

```
"Virginia Learner "/
├── server.py              # Zero-dependency Python 3 HTTP server with LAN IP & QR generator
├── run.sh                 # Convenient shell launcher
├── generate_data.py       # Builds authentic Virginia DMV signs and questions
├── test_data.py           # Automated test suite verifying schema and integrity
├── qr_generator.py        # Pure Python 3 standard library QR code SVG & ASCII generator
├── data/
│   ├── signs.json         # 38 Virginia road signs with vector SVGs & rules
│   ├── questions_signs.json   # 40 authentic Part 1 sign questions
│   ├── questions_general.json # 75 authentic Part 2 general knowledge questions
│   └── cheat_sheet.json   # Quick-reference tables of rules & numbers
└── static/
    ├── index.html         # Single Page Application shell (Kiosk + Mobile UI)
    ├── manifest.json      # PWA manifest for iPad/iPhone Home Screen
    ├── sw.js              # Service worker for offline asset caching
    ├── css/
    │   ├── style.css      # Core responsive styles & iPad touch optimizations
    │   └── kiosk.css      # Authentic Virginia DMV touch-screen kiosk theme
    ├── js/
    │   ├── app.js         # SPA router, Web Audio synthesizer, storage, network sync
    │   ├── exam.js        # Official 2-part DMV exam engine & practice engine
    │   ├── flashcards.js  # 3D interactive flashcard & sign study catalog
    │   └── speech.js      # Web Speech API audio test reader
    └── icons/
        └── icon.svg       # Virginia DMV badge vector icon
```

---

## 🧪 Verification & Testing

Run the automated data integrity test:
```bash
python3 test_data.py
```
Run the server self-test:
```bash
python3 server.py --test
```
