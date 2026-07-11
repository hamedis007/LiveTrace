import psutil
import os
import subprocess
import winreg
import json
import hashlib
from datetime import datetime



def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'username', 'status']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes

def get_network_connections():
    connections = []
    for conn in psutil.net_connections(kind='inet'):
        try:
            connections.append({
                'pid': conn.pid,
                'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                'status': conn.status
            })
        except Exception:
            pass
    return connections

def get_user_sessions():
    try:
        result = subprocess.check_output(
            'quser', 
            shell=True, 
            text=True, 
            stderr=subprocess.DEVNULL,
            encoding='utf-8',
            errors='ignore'
        )
        return result.strip()
    except Exception:
        try:
            result = subprocess.check_output(
                'whoami', 
                shell=True, 
                text=True,
                errors='ignore'
            )
            return f"Current user: {result.strip()}"
        except Exception:
            return "Could not retrieve user sessions."

def get_prefetch_files():
    prefetch_paths = [
        "C:\\Windows\\Prefetch",
        os.path.expandvars("%SystemRoot%\\Prefetch")
    ]
    prefetch_files = []
    for prefetch_path in prefetch_paths:
        try:
            if os.path.exists(prefetch_path):
                for f in os.listdir(prefetch_path):
                    if f.endswith(".pf"):
                        full_path = os.path.join(prefetch_path, f)
                        try:
                            prefetch_files.append({
                                'name': f,
                                'last_modified': datetime.fromtimestamp(
                                    os.path.getmtime(full_path)
                                ).strftime('%Y-%m-%d %H:%M:%S')
                            })
                        except Exception:
                            pass
                if prefetch_files:
                    break
        except PermissionError:
            continue
        except Exception:
            continue
    return prefetch_files

def get_registry_artifacts():
    artifacts = []
    keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
    ]
    for key_path in keys:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    artifacts.append({'key': key_path, 'name': name, 'value': value})
                    i += 1
                except OSError:
                    break
        except Exception:
            pass
    return artifacts

def get_event_logs():
    print("[*] Collecting event logs...")
    event_logs = []
    try:
        import win32evtlog
        log_types = ['System', 'Security']
        for log_type in log_types:
            try:
                hand = win32evtlog.OpenEventLog('localhost', log_type)
                flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                for event in events[:50]:
                    event_logs.append({
                        'EventID': event.EventID & 0xFFFF,
                        'TimeCreated': str(event.TimeGenerated),
                        'Channel': log_type,
                        'Message': str(event.StringInserts)[:200] if event.StringInserts else 'N/A'
                    })
                win32evtlog.CloseEventLog(hand)
            except Exception as e:
                print(f"[!] Could not read {log_type}: {e}")
                continue
    except ImportError:
        print("[!] win32evtlog not available, skipping event logs.")
    print(f"[+] Collected {len(event_logs)} event log entries.")
    return event_logs

def collect_all():
    print("[*] Starting artifact collection...")
    data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'processes': get_running_processes(),
        'network_connections': get_network_connections(),
        'user_sessions': get_user_sessions(),
        'prefetch_files': get_prefetch_files(),
        'registry_artifacts': get_registry_artifacts(),
        'event_logs': get_event_logs()
    }
    data_string = json.dumps(data, sort_keys=True, default=str)
    data_hash = hashlib.sha256(data_string.encode()).hexdigest()
    data['integrity_hash'] = data_hash
    print("[+] Artifact collection complete.")
    print(f"[+] Integrity hash (SHA-256): {data_hash}")
    return data




