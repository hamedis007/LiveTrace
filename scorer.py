WHITELISTED_PATHS = [
    'c:\\program files\\',
    'c:\\program files (x86)\\',
    'c:\\windows\\',
    'c:\\windows\\system32\\',
    'c:\\windows\\syswow64\\',
    'c:\\programdata\\microsoft\\',
    # Common legitimate AppData apps
    'appdata\\local\\programs\\microsoft vs code',
    'appdata\\local\\anthropicclaude',
    'appdata\\local\\google\\chrome',
    'appdata\\local\\microsoft\\teams',
    'appdata\\local\\discord',
    'appdata\\local\\slack',
    'appdata\\local\\zoom',
    'appdata\\local\\spotify',
    'appdata\\local\\steam',
    'appdata\\roaming\\spotify',
    'appdata\\local\\nhnotifsys',
    'appdata\\local\\packages',
]

WHITELISTED_PROCESS_NAMES = [
    'code.exe', 'claude.exe', 'chrome.exe', 'firefox.exe',
    'msedge.exe', 'teams.exe', 'discord.exe', 'slack.exe',
    'zoom.exe', 'spotify.exe', 'steam.exe', 'onedrive.exe',
    'nahimicnotifsys.exe', 'searchapp.exe', 'widgets.exe',
    'shellexperiencehost.exe', 'startmenuexperiencehost.exe',
    'securityhealthsystray.exe', 'securityhealthservice.exe',
]

def is_whitelisted(exe, name):
    exe_lower = (exe or '').lower()
    name_lower = (name or '').lower()
    for path in WHITELISTED_PATHS:
        if path in exe_lower:
            return True
    for proc_name in WHITELISTED_PROCESS_NAMES:
        if proc_name == name_lower:
            return True
    return False

def score_artifacts(data):
    print("[*] Starting suspicion scoring...")
    scored = {
        'suspicious_processes': [],
        'suspicious_connections': [],
        'suspicious_registry': [],
        'suspicious_prefetch': [],
        'total_score': 0
    }

    # Score processes
    suspicious_paths = [
        'temp', 'appdata\\local\\temp', 'downloads',
        'desktop', 'public', 'recycle'
    ]
    suspicious_names = [
        'mimikatz', 'psexec', 'netcat', 'nc.exe',
        'pwdump', 'fgdump', 'metasploit'
    ]

    for proc in data.get('processes', []):
        reasons = []
        exe = (proc.get('exe') or '').lower()
        name = (proc.get('name') or '').lower()

        if is_whitelisted(exe, name):
            continue

        for path in suspicious_paths:
            if path in exe:
                reasons.append(f"Running from suspicious path: {exe}")
                break

        for sus_name in suspicious_names:
            if sus_name in name:
                reasons.append(f"Suspicious process name: {name}")
                break

        if reasons:
            scored['suspicious_processes'].append({
                'pid': proc.get('pid'),
                'name': proc.get('name'),
                'exe': proc.get('exe'),
                'reasons': reasons
            })
            scored['total_score'] += 10

    # Score network connections
    suspicious_ports = [4444, 1337, 31337, 8080, 9001, 6666, 5555]
    for conn in data.get('network_connections', []):
        reasons = []
        remote = conn.get('remote_address') or ''

        for port in suspicious_ports:
            if f":{port}" in remote:
                reasons.append(f"Connection to suspicious port: {port}")
                break

        if reasons:
            scored['suspicious_connections'].append({
                'local': conn.get('local_address'),
                'remote': conn.get('remote_address'),
                'status': conn.get('status'),
                'reasons': reasons
            })
            scored['total_score'] += 15

    # Score registry artifacts
    legitimate_registry_names = [
        'SecurityHealth', 'OneDrive', 'Teams', 'Discord',
        'Spotify', 'Steam', 'RtkAudUService', 'NvBackend',
        'Delete Cached Update Binary', 'Delete Cached Standard Binary'
    ]
    for artifact in data.get('registry_artifacts', []):
        name = artifact.get('name', '')
        value = (artifact.get('value') or '').lower()
        reasons = []

        suspicious_value_paths = ['appdata\\local\\temp', 'downloads', '\\temp\\']
        for path in suspicious_value_paths:
            if path in value:
                reasons.append(f"Registry entry pointing to suspicious path: {value}")
                break

        if name in legitimate_registry_names:
            continue

        if reasons:
            scored['suspicious_registry'].append({
                'key': artifact.get('key'),
                'name': name,
                'value': artifact.get('value'),
                'reasons': reasons
            })
            scored['total_score'] += 20

    # Score prefetch
    suspicious_prefetch_names = [
        'MIMIKATZ', 'PSEXEC', 'NETCAT', 'PWDUMP',
        'FGDUMP', 'NC.EXE', 'METERPRETER', 'METASPLOIT'
    ]
    for pf in data.get('prefetch_files', []):
        pf_name = pf.get('name', '').upper()
        for sus in suspicious_prefetch_names:
            if sus in pf_name:
                scored['suspicious_prefetch'].append({
                    'name': pf.get('name'),
                    'last_modified': pf.get('last_modified'),
                    'reason': f"Known malicious tool detected in prefetch: {sus}"
                })
                scored['total_score'] += 25
                break

    print(f"[+] Scoring complete. Total suspicion score: {scored['total_score']}")
    return scored
