LiveTrace — Live System Forensics & Triage Toolkit
LiveTrace is a lightweight, Python-based automated live forensic triage toolkit for Windows. It collects forensic artefacts from a live Windows system, applies a rule-based suspicion scoring engine, and presents findings through an interactive web dashboard and a structured PDF report — all in a single execution with no installation or licensing required.
Features

Collects 6 artefact categories: running processes, network connections, user sessions, prefetch files, Windows event logs, and registry startup entries
Rule-based suspicion scoring engine with weighted indicators
Interactive Flask web dashboard served at http://127.0.0.1:5000
Structured PDF forensic report generated automatically
SHA-256 integrity hash embedded in both outputs for evidence verification
Standalone executable via PyInstaller — no Python required on target machine

Requirements

Windows 10 or Windows 11
Python 3.12
Administrator privileges

Installation
pip install -r requirements.txt
Usage
Run as administrator:
python livetrace.py
The browser will open automatically at http://127.0.0.1:5000
Output Files

LiveTrace_Report.pdf — PDF forensic report
LiveTrace_Log.json — JSON log of all collected artefacts

Project Structure
LiveTrace/
├── livetrace.py          # Main orchestrator and Flask application
├── collector.py          # Artefact collection module
├── scorer.py             # Suspicion scoring engine
├── reporter.py           # PDF report generator
├── requirements.txt      # Python dependencies
├── templates/
│   └── dashboard.html    # Flask web dashboard template
└── static/
    └── chart.min.js      # Chart.js library (local)


Academic Context
Developed as a graduation project for BSc (Hons) Computer Security and Forensics at the Global College of Engineering and Technology (GCET), affiliated with UWE Bristol.
