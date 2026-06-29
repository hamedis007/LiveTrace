import os
import sys
import json
import subprocess
import threading
import webbrowser
from flask import Flask, render_template, send_file
from collector import collect_all
from scorer import score_artifacts
from scorer import get_risk
from reporter import generate_report


def print_banner():
    print("""
    ██╗     ██╗██╗   ██╗███████╗████████╗██████╗  █████╗  ██████╗███████╗
    ██║     ██║██║   ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝
    ██║     ██║██║   ██║█████╗     ██║   ██████╔╝███████║██║     █████╗  
    ██║     ██║╚██╗ ██╔╝██╔══╝     ██║   ██╔══██╗██╔══██║██║     ██╔══╝  
    ███████╗██║ ╚████╔╝ ███████╗   ██║   ██║  ██║██║  ██║╚██████╗███████╗
    ╚══════╝╚═╝  ╚═══╝  ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝
    """)
    print("    Live System Forensics & Triage Toolkit")
    print("    ----------------------------------------\n")

def kill_port(port):
    import subprocess
    result = subprocess.run(f'netstat -ano | findstr :{port}', shell=True, capture_output=True, text=True)
    for line in result.stdout.strip().split('\n'):
        if 'LISTENING' in line:
            pid = line.strip().split()[-1]
            subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=False)

def main():
    
    kill_port(5000)
    print_banner()
    print("[*] LiveTrace initializing...\n")
    

    data = collect_all()
    print()

    scored = score_artifacts(data)
    print()

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "LiveTrace_Log.json")
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4, default=str)
    print(f"[+] JSON log saved to: {json_path}")
    print()

    report_path = generate_report(data, scored)
    print()

    print("[*] Launching dashboard...")
    print("[*] Opening browser at http://127.0.0.1:5000")
    print("[*] Press Ctrl+C to stop LiveTrace\n")


    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    app = Flask(__name__,
                template_folder=os.path.join(base_path, 'templates'),
                static_folder=os.path.join(base_path, 'static'),
                static_url_path='/static')


    @app.route('/')
    def dashboard():
        risk_level = get_risk(scored['total_score'])
        risk_class = risk_level.lower()
        return render_template('dashboard.html',
                            data=data,
                            scored=scored,
                            risk_level=risk_level,
                            risk_class=risk_class)

    @app.route('/download')
    def download():
        return send_file(report_path, as_attachment=True)

    @app.route('/download_json')
    def download_json():
        return send_file(json_path, as_attachment=True)

    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open_new('http://127.0.0.1:5000')

    threading.Timer(1.5, open_browser).start()
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == "__main__":
    main()