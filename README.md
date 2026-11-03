# AI-POWERED INTELLIGENT ONLINE EXAMINATION AND SECURE ASSESSMENT SYSTEM
### WITH ADAPTIVE TESTING, BEHAVIORAL MONITORING AND LEARNING ANALYTICS

**A Project Report Implementation**  
**Submitted by:** VIDUSHI [25MCI10158]  
**Degree:** Master of Computer Applications (MCA)  
**Institution:** Chandigarh University, Mohali (2026-2027)  

---

## 📌 Project Overview
This project is an end-to-end, privacy-preserving, camera-free intelligent assessment and examination portal built in accordance with the Chandigarh University MCA Final Year Project Report. 

Instead of intrusive webcam surveillance, the platform uses an **Explainable Digital Behavioral Monitoring Engine** and introduces a **Realistic Human-Like AI Invigilator Avatar (Dr. Sarah)** who speaks instructions, monitors browser interactions, detects room acoustics, and conducts interactive verbal viva voce examinations.

---

## ✨ 5-6 Key Extra Features Implemented

1. **Realistic Human-Like AI Avatar Proctor (Dr. Sarah):**
   - High-fidelity 2.5D HTML5 Canvas rendering of a human invigilator with lifelike eye tracking (saccades), double-blinking physics, and natural facial expressions (*Neutral, Speaking, Warning, Listening, Approving*).
   - Real-time phonetic **Lip-Sync mouth articulation** synchronized with Web Speech API voice synthesis.
   - Speaks exam guidelines, reads questions aloud, and issues proactive verbal warnings when violations occur.

2. **Camera-Free Acoustic / Noise Anomaly Proctoring:**
   - Uses Web Audio API frequency analysis to detect sudden room chatter, loud noises, or whispers without capturing video, preserving complete privacy.

3. **Keystroke Dynamics & Biometric Typing Cadence:**
   - Tracks key flight time, dwell time, and flags automated bots, rapid copy-paste injections, and typing anomalies.

4. **Interactive AI Avatar Oral Viva Voce Mode:**
   - Dedicated oral examination mode where Dr. Sarah speaks questions aloud and listens to student voice responses via speech-to-text recognition, providing instant conceptual AI grading and feedback.

5. **Offline Resilience & Network Disruption Auto-Sync:**
   - Stores unsubmitted answers in browser local storage if internet drops; automatically synchronizes with the server once connection is restored.

6. **Tamper-Proof Cryptographic Result Hash (SHA-256) & Public Verification Portal:**
   - Every completed exam generates a unique cryptoseal hash and verification ID. Anyone can verify the authenticity of a certificate through the `/verify` portal.

7. **Teacher Real-Time Command Center:**
   - Live dashboard showing real-time risk scores of active students with a 1-click broadcast tool that sends an audio warning straight to the student's exam avatar.

8. **Psychometric Item Analysis & Adaptive IRT Engine:**
   - Evaluates Question Difficulty Index ($P$), Discrimination Index ($D$), and applies Item Response Theory (Rasch 1PL) ability estimation ($\theta$).

---

## 💻 How to Run in VS Code (Step-by-Step Hindi & English)

### 1️⃣ Step 1: Open the Project in VS Code
1. Open **Visual Studio Code**.
2. Click on **File** ➔ **Open Folder...**
3. Select the project folder:
   `C:\Users\vidus\.gemini\antigravity\scratch\ai_exam_system`
   *(or the extracted ZIP folder)*.

### 2️⃣ Step 2: Open Terminal in VS Code
- In VS Code, press `Ctrl + ~` (tilde) or click **Terminal ➔ New Terminal**.

### 3️⃣ Step 3: Check / Install Requirements
Run the following command in the VS Code terminal:
```bash
pip install -r requirements.txt
```
*(Note: Flask is the only lightweight requirement. SQLite3 and math/hashlib are already built into Python!)*

### 4️⃣ Step 4: Run the Application
Run:
```bash
python app.py
```
*Alternately, double-click the `run.bat` file in Windows Explorer!*

### 5️⃣ Step 5: Open in Web Browser
Open your browser (Chrome / Edge / Firefox) and visit:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Accounts

| Role | Username | Password | Full Name & Details |
| :--- | :--- | :--- | :--- |
| **Student** | `vidushi` | `password123` | **Vidushi (25MCI10158)** - MCA Chandigarh University |
| **Teacher** | `teacher` | `password123` | **Prof. Dr. A. K. Verma** - Exam Studio & Live Command Center |
| **Admin** | `admin` | `admin123` | **University Exam Superintendent** - System Audit Logs |

*(Tip: On the login page, you can also use the 1-click Quick Demo buttons to log in instantly!)*

---

## 📂 Project Architecture

```
ai_exam_system/
├── app.py                     # Flask application server & API endpoints
├── database.py                # SQLite schema and seed data
├── ai_engine.py               # IRT Engine, NLP duplicate checker, ML performance predictor
├── exam_system.db             # Pre-configured SQLite database
├── requirements.txt           # Minimal dependencies
├── run.bat                    # 1-click launcher for Windows
├── run.sh                     # 1-click launcher for Linux/Mac
├── README.md                  # Project documentation & guide
├── static/
│   ├── css/
│   │   ├── style.css          # Modern CU Crimson branding and glassmorphic styling
│   │   └── avatar.css         # Styling for AI Avatar, aura glow & speech bubble
│   └── js/
│       ├── avatar.js          # Realistic 2.5D Canvas human avatar with Lip-Sync
│       ├── audio_monitor.js   # Camera-free acoustic anomaly detector
│       ├── keystroke.js       # Typing biometrics & cadence analyzer
│       ├── exam.js            # Exam runner (fullscreen, tab tracking, offline sync)
│       ├── viva.js            # Interactive spoken viva voce assessment
│       └── teacher_live.js    # Real-time live invigilator monitor
└── templates/
    ├── base.html              # Base template with CU header & navbar
    ├── login.html             # Multi-role authentication with demo logins
    ├── student_dashboard.html # Student analytics, ML predictions, radar chart
    ├── exam_screen.html       # Fullscreen exam with AI Avatar & camera-free surveillance
    ├── viva_screen.html       # AI Avatar oral examination mode
    ├── exam_result.html       # Official certificate with SHA-256 hash & integrity audit
    ├── teacher_dashboard.html # Question bank, NLP duplicate checker, item analysis
    ├── teacher_live.html      # Real-time command center & live warning broadcast
    ├── teacher_review.html    # AI descriptive answer grading review
    ├── admin_dashboard.html   # System audit logs & security analytics
    └── verify_cert.html       # Public cryptographic certificate verification portal
```

---

## 🎓 Academic Conformity
This project conforms with all requirements of the MCA Final Semester Project Report at **Chandigarh University, Mohali (2026-2027)** for candidate **VIDUSHI (25MCI10158)**.
