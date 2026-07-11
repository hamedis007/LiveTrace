from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os
from scorer import get_risk


DARK_NAVY = colors.HexColor('#1a1a2e')
ACCENT_BLUE = colors.HexColor('#4a4a8a')
LIGHT_BLUE = colors.HexColor('#7a7aff')
RED = colors.HexColor('#c0392b')
GREEN = colors.HexColor('#27ae60')
ORANGE = colors.HexColor('#f39c12')
LIGHT_GRAY = colors.HexColor('#f5f5f5')
MID_GRAY = colors.HexColor('#cccccc')
DARK_GRAY = colors.HexColor('#444444')
WHITE = colors.white

def build_styles():
    styles = {}
    styles['logo'] = ParagraphStyle('logo', fontSize=32, alignment=TA_CENTER,
                                     textColor=LIGHT_BLUE, fontName='Helvetica-Bold',
                                     spaceAfter=2, leading=36)
    styles['tagline'] = ParagraphStyle('tagline', fontSize=9, alignment=TA_CENTER,
                                        textColor=colors.HexColor('#aaaacc'), spaceAfter=2,
                                        fontName='Helvetica', leading=12)
    styles['timestamp'] = ParagraphStyle('timestamp', fontSize=8, alignment=TA_CENTER,
                                          textColor=colors.HexColor('#888888'), spaceAfter=0)
    styles['section'] = ParagraphStyle('section', fontSize=12, textColor=DARK_NAVY,
                                        spaceAfter=6, spaceBefore=12,
                                        fontName='Helvetica-Bold',
                                        borderPad=4)
    styles['normal'] = ParagraphStyle('normal', fontSize=8, spaceAfter=3,
                                       leading=12, textColor=DARK_GRAY)
    styles['alert'] = ParagraphStyle('alert', fontSize=8, textColor=RED,
                                      spaceAfter=3, leading=12, fontName='Helvetica-Bold')
    styles['small'] = ParagraphStyle('small', fontSize=7, textColor=DARK_GRAY,
                                      spaceAfter=2, leading=10)
    styles['ok'] = ParagraphStyle('ok', fontSize=10, textColor=GREEN,
                                   fontName='Helvetica-Bold')
    styles['footer'] = ParagraphStyle('footer', fontSize=7, alignment=TA_CENTER,
                                       textColor=ACCENT_BLUE)
    return styles


def standard_table_style(header_color=DARK_NAVY):
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, MID_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_GRAY, WHITE]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])

def generate_report(data, scored, output_path=None):
    if output_path is None:
        import sys
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, "LiveTrace_Report.pdf")
    print("[*] Generating PDF report...")
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.65*inch,
        leftMargin=0.65*inch,
        topMargin=0.5*inch,
        bottomMargin=0.65*inch
    )

    styles = build_styles()
    elements = []
    page_width = A4[0] - 1.3*inch
    risk_level = get_risk(scored['total_score'])
    risk_colors = {"LOW": GREEN, "MEDIUM": ORANGE, "HIGH": RED}
    risk_color = risk_colors[risk_level]


    header_content = [
        [Paragraph("[ LiveTrace ]", styles['logo'])],
        [Paragraph("LIVE SYSTEM FORENSICS &amp; TRIAGE TOOLKIT", styles['tagline'])],
        [Paragraph(f"Report Generated: {data['timestamp']}", styles['timestamp'])],
    ]
    header_table = Table(header_content, colWidths=[page_width])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, 0), 20),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 16),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, 1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 2),
        ('TOPPADDING', (0, 2), (-1, 2), 2),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 12))


    elements.append(Paragraph("Investigation Summary", styles['section']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
    elements.append(Spacer(1, 6))


    score_color = risk_color

    summary_top = [['Suspicion Score', 'Risk Level', 'Suspicious Processes',
                     'Suspicious Connections', 'Suspicious Registry', 'Suspicious Prefetch']]
    summary_bottom = [[
        str(scored['total_score']),
        risk_level,
        str(len(scored['suspicious_processes'])),
        str(len(scored['suspicious_connections'])),
        str(len(scored['suspicious_registry'])),
        str(len(scored['suspicious_prefetch']))
    ]]

    col_w = page_width / 6
    summary_style = TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), DARK_NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, 0), 4),
        ('RIGHTPADDING', (0, 0), (-1, 0), 4),

        ('BACKGROUND', (0, 1), (-1, 1), WHITE),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, 1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, 1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 10),

        ('TEXTCOLOR', (0, 1), (0, 1), score_color),

        ('BACKGROUND', (1, 1), (1, 1), risk_color),
        ('TEXTCOLOR', (1, 1), (1, 1), WHITE),

        ('TEXTCOLOR', (2, 1), (-1, 1), ACCENT_BLUE),

        ('GRID', (0, 0), (-1, -1), 0.4, MID_GRAY),
        ('BOX', (0, 0), (-1, -1), 1, ACCENT_BLUE),
    ])

    full_summary = [summary_top[0], summary_bottom[0]]
    summary_table = Table(full_summary, colWidths=[col_w] * 6)
    summary_table.setStyle(summary_style)
    elements.append(summary_table)

    elements.append(Spacer(1, 8))
    hash_box = Table(
        [[
            Paragraph("Hash (SHA-256):", ParagraphStyle(
                'hl', fontSize=8, textColor=WHITE, fontName='Helvetica-Bold')),
            Paragraph(str(data.get('integrity_hash', 'N/A')), ParagraphStyle(
                'hv', fontSize=8, textColor=GREEN, fontName='Helvetica',
                wordWrap='CJK'))
        ]],
        colWidths=[2.2*inch, page_width - 2.2*inch]
    )
    hash_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_NAVY),
        ('BOX', (0, 0), (-1, -1), 1, ACCENT_BLUE),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(hash_box)
    elements.append(Spacer(1, 14))
    

    elements.append(Spacer(1, 8))
    cards_data = [[
        Paragraph("Running Processes", ParagraphStyle('cl', fontSize=7, textColor=WHITE,
                  alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("Network Connections", ParagraphStyle('cl', fontSize=7, textColor=WHITE,
                  alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("Prefetch Files", ParagraphStyle('cl', fontSize=7, textColor=WHITE,
                  alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("Registry Artifacts", ParagraphStyle('cl', fontSize=7, textColor=WHITE,
                  alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("User Session", ParagraphStyle('cl', fontSize=7, textColor=WHITE,
                  alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph("Event Logs", ParagraphStyle('cl', fontSize=7, textColor=WHITE,
                  alignment=TA_CENTER, fontName='Helvetica-Bold')),
    ],[
        Paragraph(str(len(data['processes'])), ParagraphStyle('cv', fontSize=18,
                  textColor=LIGHT_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph(str(len(data['network_connections'])), ParagraphStyle('cv', fontSize=18,
                  textColor=LIGHT_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph(str(len(data['prefetch_files'])), ParagraphStyle('cv', fontSize=18,
                  textColor=LIGHT_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph(str(len(data['registry_artifacts'])), ParagraphStyle('cv', fontSize=18,
                  textColor=LIGHT_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph(str(data.get('user_sessions', 'N/A')).split(':')[-1].strip(),
                  ParagraphStyle('cv', fontSize=10, textColor=LIGHT_BLUE,
                  alignment=TA_CENTER, fontName='Helvetica-Bold')),
        Paragraph(str(len(data.get('event_logs', []))), ParagraphStyle('cv', fontSize=18,
                  textColor=LIGHT_BLUE, alignment=TA_CENTER, fontName='Helvetica-Bold')),
    ]]

    col_w2 = page_width / 6
    cards_table = Table(cards_data, colWidths=[col_w2] * 6)
    cards_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_BLUE),
        ('BACKGROUND', (0, 1), (-1, 1), DARK_NAVY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 1), (-1, 1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#2a2a4a')),
        ('BOX', (0, 0), (-1, -1), 1, ACCENT_BLUE),
    ]))
    elements.append(cards_table)
    elements.append(Spacer(1, 14))


    elements.append(Paragraph("Suspicious Findings", styles['section']))
    elements.append(HRFlowable(width="100%", thickness=1, color=RED if scored['suspicious_processes'] else MID_GRAY))
    elements.append(Spacer(1, 6))

    if scored['suspicious_processes'] or scored['suspicious_connections'] or \
       scored['suspicious_registry'] or scored['suspicious_prefetch']:
        
        all_findings = [
            ('Process', scored['suspicious_processes'], 
             lambda f: f"PID {f['pid']} — {f['name']}", 
             lambda f: f"Path: {f.get('exe', 'N/A')}"),
            ('Connection', scored['suspicious_connections'], 
             lambda f: f"Connection — {f.get('remote', 'N/A')}", 
             lambda f: f"Status: {f.get('status', 'N/A')}"),
            ('Registry', scored['suspicious_registry'], 
             lambda f: f"Registry — {f.get('name', 'N/A')}", 
             lambda f: f"Value: {f.get('value', 'N/A')}"),
            ('Prefetch', scored['suspicious_prefetch'], 
             lambda f: f"Prefetch — {f.get('name', 'N/A')}", 
             lambda f: f"Last Modified: {f.get('last_modified', 'N/A')}"),
        ]

        for category, findings, title_fn, subtitle_fn in all_findings:
            for finding in findings:
                reasons = finding.get('reasons', [finding.get('reason', '')])
                alert_content = [
                    [Paragraph(title_fn(finding),
                               ParagraphStyle('ah', fontSize=8, fontName='Helvetica-Bold', textColor=RED)),
                     Paragraph(subtitle_fn(finding),
                               ParagraphStyle('ap', fontSize=7, textColor=DARK_GRAY))],
                ]
                for reason in reasons:
                    alert_content.append([
                        Paragraph(f"! {reason}", styles['alert']),
                        Paragraph("", styles['small'])
                    ])
                alert_table = Table(alert_content, colWidths=[2.3*inch, page_width - 2.3*inch])
                alert_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff5f5')),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('BOX', (0, 0), (-1, -1), 1, RED),
                    ('LINEBEFORE', (0, 0), (0, -1), 3, RED),
                ]))
                elements.append(alert_table)
                elements.append(Spacer(1, 4))

    else:
        elements.append(Paragraph("✓ No suspicious findings detected on this system.", styles['ok']))

    elements.append(Spacer(1, 10))


    elements.append(Paragraph("Running Processes", styles['section']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"Total processes collected: {len(data['processes'])}",
                               styles['small']))
    elements.append(Spacer(1, 4))

    proc_data = [['PID', 'Process Name', 'Status', 'User', 'Executable Path']]
    for proc in data['processes'][:60]:
        username = proc.get('username') or 'N/A'
        proc_data.append([
            str(proc.get('pid', '')),
            str(proc.get('name', '') or 'N/A')[:28],
            str(proc.get('status', '') or 'N/A'),
            str(username)[:20],
            str(proc.get('exe', '') or 'N/A')[:65],
        ])
    proc_table = Table(proc_data,
                       colWidths=[0.45*inch, 1.5*inch, 0.65*inch, 1.4*inch, 3.3*inch])
    proc_table.setStyle(standard_table_style())
    elements.append(proc_table)
    elements.append(Spacer(1, 14))


    elements.append(Paragraph("Network Connections", styles['section']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"Total connections collected: {len(data['network_connections'])}",
                               styles['small']))
    elements.append(Spacer(1, 4))

    net_data = [['Local Address', 'Remote Address', 'Status', 'PID']]
    for conn in data['network_connections'][:40]:
        net_data.append([
            str(conn.get('local_address', '') or 'N/A'),
            str(conn.get('remote_address', '') or 'N/A'),
            str(conn.get('status', '') or 'N/A'),
            str(conn.get('pid', '') or 'N/A'),
        ])
    net_table = Table(net_data,
                      colWidths=[2.2*inch, 2.2*inch, 1.1*inch, 0.8*inch])
    net_table.setStyle(standard_table_style())
    elements.append(net_table)
    elements.append(Spacer(1, 14))


    elements.append(Paragraph("User Sessions", styles['section']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
    elements.append(Spacer(1, 4))
    session_box = Table(
        [[Paragraph(str(data.get('user_sessions', 'N/A')), styles['normal'])]],
        colWidths=[page_width]
    )
    session_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
        ('BOX', (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(session_box)
    elements.append(Spacer(1, 14))


    elements.append(Paragraph("Registry Artifacts", styles['section']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
    elements.append(Spacer(1, 4))

    if data['registry_artifacts']:
        reg_data = [['Registry Key', 'Entry Name', 'Value']]
        for artifact in data['registry_artifacts']:
            reg_data.append([
                str(artifact.get('key', '') or 'N/A'),
                str(artifact.get('name', '') or 'N/A')[:25],
                str(artifact.get('value', '') or 'N/A')[:55],
            ])
        reg_table = Table(reg_data, colWidths=[2.3*inch, 1.3*inch, 2.7*inch])
        reg_table.setStyle(standard_table_style())
        elements.append(reg_table)
    else:
        elements.append(Paragraph("No registry artifacts found.", styles['normal']))
    elements.append(Spacer(1, 14))


    elements.append(Paragraph("Prefetch Files (Most Recent 50)", styles['section']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
    elements.append(Spacer(1, 4))

    if data['prefetch_files']:
        pf_data = [['Filename', 'Last Modified']]
        sorted_pf = sorted(data['prefetch_files'],
                           key=lambda x: x.get('last_modified', ''), reverse=True)[:50]
        for pf in sorted_pf:
            pf_data.append([
                str(pf.get('name', '') or 'N/A'),
                str(pf.get('last_modified', '') or 'N/A'),
            ])
        pf_table = Table(pf_data, colWidths=[4.0*inch, 2.3*inch])
        pf_table.setStyle(standard_table_style())
        elements.append(pf_table)
    else:
        elements.append(Paragraph(
            "No prefetch files found. Run LiveTrace as Administrator to collect prefetch data.",
            styles['normal']))

    elements.append(Paragraph("Event Logs", styles['section']))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
    elements.append(Spacer(1, 4))

    if data.get('event_logs'):
        el_data = [['Event ID', 'Level', 'Time Created', 'Channel', 'Message']]
        for log in data['event_logs'][:50]:
            el_data.append([
                str(log.get('EventID', 'N/A')),
                str(log.get('Level', 'N/A')),
                str(log.get('TimeCreated', 'N/A')),
                str(log.get('Channel', 'N/A')),
                str(log.get('Message', 'N/A'))[:60],
            ])
        el_table = Table(el_data, colWidths=[0.6*inch, 0.6*inch, 1.4*inch, 0.7*inch, 2.9*inch])
        el_table.setStyle(standard_table_style())
        elements.append(el_table)
    else:
        elements.append(Paragraph(
            "No event logs collected. Run LiveTrace as Administrator to collect event log data.",
            styles['normal']))
    
    
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "Generated by [ LiveTrace ] — Live System Forensics &amp; Triage Toolkit | For investigative use only",
        styles['footer']
    ))

    doc.build(elements)
    print(f"[+] Report saved to: {output_path}")
    return output_path