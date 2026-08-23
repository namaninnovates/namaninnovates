import json, math, os

token = os.environ.get("GITHUB_TOKEN", "")
headers = {"Authorization": f"Bearer {token}"} if token else {}

query = """
query {
  user(login: "namaninnovates") {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
"""

try:
    import urllib.request
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers}
    )
    with urllib.request.urlopen(req) as resp:
        raw_data = json.loads(resp.read().decode("utf-8"))
    cal = raw_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
except Exception as e:
    print(f"Direct API call failed ({e}), checking local fallback...")
    fallback_file = os.path.join(os.path.dirname(__file__), "../../../scratch/contributions.json")
    if os.path.exists(fallback_file):
        with open(fallback_file, "r") as f:
            raw_data = json.load(f)
        cal = raw_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    else:
        raise e

total_commits = cal["totalContributions"]
weeks = cal["weeks"]
num_weeks = len(weeks)

SVG_W, SVG_H = 1000, 520
CX, CY = 500, 270
R_MIN = 60
R_MAX = 195

svg_lines = []
svg_lines.append(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="100%" height="100%">
  <defs>
    <style>
      .mono {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }}
      @keyframes radarSweep {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
      }}
      .radar-beam {{
        transform-origin: {CX}px {CY}px;
        animation: radarSweep 8s linear infinite;
      }}
      @keyframes pulseHub {{
        0% {{ r: 4; opacity: 1; }}
        100% {{ r: 24; opacity: 0; }}
      }}
      .hub-pulse {{
        animation: pulseHub 3s cubic-bezier(0.2, 0.8, 0.2, 1) infinite;
      }}
    </style>
    <radialGradient id="sweepGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- Pure Black Background -->
  <rect width="{SVG_W}" height="{SVG_H}" fill="#000000" stroke="#222222" stroke-width="1"/>

  <!-- Corner Brackets -->
  <path d="M 25 12 L 15 12 L 15 22" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>
  <path d="M {SVG_W - 25} 12 L {SVG_W - 15} 12 L {SVG_W - 15} 22" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>
  <path d="M 25 {SVG_H - 12} L 15 {SVG_H - 12} L 15 {SVG_H - 22}" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>
  <path d="M {SVG_W - 25} {SVG_H - 12} L {SVG_W - 15} {SVG_H - 12} L {SVG_W - 15} {SVG_H - 22}" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>

  <!-- Header -->
  <rect x="15" y="12" width="{SVG_W - 30}" height="32" fill="#000000" stroke="#222222" stroke-width="1"/>
  <text x="28" y="32" fill="#FFFFFF" font-size="12" font-weight="700" class="mono" letter-spacing="1">RADIAL RADAR TELEMETRY // 360° POLAR HEATMAP</text>
  <text x="{SVG_W - 350}" y="32" fill="#888888" font-size="10" font-weight="600" class="mono">TOTAL: {total_commits} COMMITS | 52 WEEKS RANGE</text>

  <!-- Radar Dial Rings (7 Concentric Weekday Orbits) -->
""")

for d in range(7):
    r = R_MIN + (d / 6.0) * (R_MAX - R_MIN)
    svg_lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{r:.1f}" fill="none" stroke="#181818" stroke-width="1"/>\n')

svg_lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{R_MAX + 15}" fill="none" stroke="#333333" stroke-width="1" stroke-dasharray="3 3"/>\n')
svg_lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{R_MIN - 12}" fill="none" stroke="#333333" stroke-width="1"/>\n')

months = ["AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL"]
for m_idx in range(12):
    angle_deg = m_idx * 30.0 - 90.0
    angle_rad = math.radians(angle_deg)
    x1 = CX + (R_MIN - 12) * math.cos(angle_rad)
    y1 = CY + (R_MIN - 12) * math.sin(angle_rad)
    x2 = CX + (R_MAX + 15) * math.cos(angle_rad)
    y2 = CY + (R_MAX + 15) * math.sin(angle_rad)
    svg_lines.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#222222" stroke-width="1"/>\n')
    lx = CX + (R_MAX + 30) * math.cos(angle_rad)
    ly = CY + (R_MAX + 30) * math.sin(angle_rad) + 3.5
    svg_lines.append(f'  <text x="{lx:.1f}" y="{ly:.1f}" fill="#888888" font-size="9" font-weight="700" text-anchor="middle" class="mono">{months[m_idx]}</text>\n')

deg_labels = [("000°", -90), ("090°", 0), ("180°", 90), ("270°", 180)]
for d_txt, d_ang in deg_labels:
    a_rad = math.radians(d_ang)
    dx = CX + (R_MIN - 24) * math.cos(a_rad)
    dy = CY + (R_MIN - 24) * math.sin(a_rad) + 3
    svg_lines.append(f'  <text x="{dx:.1f}" y="{dy:.1f}" fill="#555555" font-size="7.5" font-weight="600" text-anchor="middle" class="mono">{d_txt}</text>\n')

svg_lines.append(f"""
  <!-- Rotating Radar Sweep Line -->
  <g class="radar-beam">
    <line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R_MAX - 15}" stroke="#FFFFFF" stroke-width="1.2" opacity="0.6"/>
    <path d="M {CX} {CY} L {CX - 35} {CY - R_MAX - 15} A {R_MAX + 15} {R_MAX + 15} 0 0 1 {CX} {CY - R_MAX - 15} Z" fill="url(#sweepGrad)" opacity="0.4"/>
  </g>
""")

svg_lines.append('\n  <!-- 365-Day Polar Contribution Cells -->\n  <g>\n')

for w_idx, week in enumerate(weeks):
    frac_w = w_idx / float(num_weeks)
    angle_rad = frac_w * 2 * math.pi - math.pi / 2
    for day in week["contributionDays"]:
        count = day["contributionCount"]
        d_idx = (day["weekday"] + 6) % 7
        r = R_MIN + (d_idx / 6.0) * (R_MAX - R_MIN)
        px = CX + r * math.cos(angle_rad)
        py = CY + r * math.sin(angle_rad)
        if count == 0:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="1.1" fill="#222222"/>\n')
        elif count < 5:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="1.8" fill="#666666"/>\n')
        elif count < 15:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="2.5" fill="#AAAAAA"/>\n')
        elif count < 30:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="3.4" fill="#FFFFFF"/>\n')
        else:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="#FFFFFF"/>\n')
            sp_r = R_MAX + 8 + min(count, 50) * 0.4
            sp_x = CX + sp_r * math.cos(angle_rad)
            sp_y = CY + sp_r * math.sin(angle_rad)
            svg_lines.append(f'    <line x1="{px:.1f}" y1="{py:.1f}" x2="{sp_x:.1f}" y2="{sp_y:.1f}" stroke="#FFFFFF" stroke-width="1.2"/>\n')
            svg_lines.append(f'    <circle cx="{sp_x:.1f}" cy="{sp_y:.1f}" r="1.5" fill="#FFFFFF"/>\n')

svg_lines.append(f"""  </g>

  <!-- Center Radar Hub -->
  <circle cx="{CX}" cy="{CY}" r="4" fill="none" stroke="#FFFFFF" stroke-width="1" class="hub-pulse"/>
  <circle cx="{CX}" cy="{CY}" r="3" fill="#FFFFFF"/>
  <line x1="{CX - 8}" y1="{CY}" x2="{CX + 8}" y2="{CY}" stroke="#FFFFFF" stroke-width="1"/>
  <line x1="{CX}" y1="{CY - 8}" x2="{CX}" y2="{CY + 8}" stroke="#FFFFFF" stroke-width="1"/>

  <!-- Left & Right Metrics HUD Sidebars -->
  <g class="mono">
    <rect x="35" y="180" width="135" height="70" fill="#000000" stroke="#222222" stroke-width="1"/>
    <text x="45" y="200" fill="#888888" font-size="8.5" font-weight="600">// SCAN RANGE</text>
    <text x="45" y="218" fill="#FFFFFF" font-size="13" font-weight="700">360° / 52 WKS</text>
    <text x="45" y="236" fill="#666666" font-size="8">RESOLUTION: 7-DAY ORBIT</text>

    <rect x="{SVG_W - 170}" y="180" width="135" height="70" fill="#000000" stroke="#222222" stroke-width="1"/>
    <text x="{SVG_W - 160}" y="200" fill="#888888" font-size="8.5" font-weight="600">// TOTAL ACTIVITY</text>
    <text x="{SVG_W - 160}" y="218" fill="#FFFFFF" font-size="13" font-weight="700">{total_commits} COMMITS</text>
    <text x="{SVG_W - 160}" y="236" fill="#666666" font-size="8">MAX PEAK: 65 COMMITS/D</text>
  </g>

  <!-- Footer Bar -->
  <rect x="15" y="{SVG_H - 32}" width="{SVG_W - 30}" height="22" fill="#000000" stroke="#222222" stroke-width="1"/>
  <text x="26" y="{SVG_H - 17}" fill="#888888" font-size="9.5" font-weight="600" class="mono">// POLAR TELEMETRY RADAR | RANGE: 0–65 COMMITS | GITHUB.COM/NAMANINNOVATES</text>
</svg>
""")

target_path = os.path.join(os.path.dirname(__file__), "../assets/radial_radar_heatmap.svg")
os.makedirs(os.path.dirname(target_path), exist_ok=True)
with open(target_path, "w") as f:
    f.writelines(svg_lines)

print("Radial Radar SVG updated at:", target_path)
