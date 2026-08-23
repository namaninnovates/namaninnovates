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
    fallback_file = os.path.join(os.path.dirname(__file__), "contributions.json")
    if os.path.exists(fallback_file):
        with open(fallback_file, "r") as f:
            raw_data = json.load(f)
        cal = raw_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    else:
        raise e

total_commits = cal["totalContributions"]
weeks = cal["weeks"]
num_weeks = len(weeks)

WIDTH, HEIGHT = 1000, 520
CX, CY = 500, 270
R_MIN = 60
R_MAX = 195

PANEL_BG = "#161b22"
BORDER_DEFAULT = "#30363d"
BORDER_MUTED = "#21262d"
TEXT_PRIMARY = "#f0f6fc"
TEXT_MUTED = "#8b949e"

svg_lines = []
svg_lines.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%">
  <defs>
    <style>
      .code-mono {{
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }}
      @keyframes pulseWave {{
        0% {{ r: {R_MIN}px; stroke-opacity: 0.9; }}
        100% {{ r: {R_MAX + 15}px; stroke-opacity: 0; }}
      }}
      @keyframes beaconFlash {{
        0%, 100% {{ r: 5.2px; fill-opacity: 0.85; }}
        50% {{ r: 7.2px; fill-opacity: 1; }}
      }}
      @keyframes midFlash {{
        0%, 100% {{ r: 3.6px; fill-opacity: 0.8; }}
        50% {{ r: 4.8px; fill-opacity: 1; }}
      }}
      @keyframes hubPulse {{
        0% {{ r: 4px; stroke-opacity: 0.9; }}
        100% {{ r: 32px; stroke-opacity: 0; }}
      }}
      .wave-1 {{ animation: pulseWave 3s cubic-bezier(0.1, 0.8, 0.2, 1) infinite; }}
      .wave-2 {{ animation: pulseWave 3s cubic-bezier(0.1, 0.8, 0.2, 1) infinite 1s; }}
      .wave-3 {{ animation: pulseWave 3s cubic-bezier(0.1, 0.8, 0.2, 1) infinite 2s; }}
      .hub-shockwave {{ animation: hubPulse 2.2s cubic-bezier(0.2, 0.8, 0.2, 1) infinite; }}
      .beacon-high {{ animation: beaconFlash 2s ease-in-out infinite; }}
      .beacon-mid {{ animation: midFlash 2.8s ease-in-out infinite; }}
    </style>
    <radialGradient id="radarSweepWedge" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{TEXT_PRIMARY}" stop-opacity="0.28"/>
      <stop offset="60%" stop-color="{TEXT_PRIMARY}" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="{TEXT_PRIMARY}" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- 100% Transparent Outer Frame -->
  <rect width="{WIDTH}" height="{HEIGHT}" rx="6" fill="none" stroke="{BORDER_DEFAULT}" stroke-width="1"/>

  <!-- Header Bar -->
  <rect x="15" y="12" width="{WIDTH - 30}" height="32" rx="4" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
  <text x="28" y="32" fill="{TEXT_PRIMARY}" font-size="12" font-weight="600" class="code-mono" letter-spacing="0.5">RADIAL CONTRIBUTION RADAR // 360° ACTIVE VECTOR SWEEP</text>
  <text x="{WIDTH - 325}" y="32" fill="{TEXT_MUTED}" font-size="10" font-weight="500" class="code-mono">TOTAL: {total_commits} COMMITS | 52 WEEKS ACTIVE</text>

  <!-- Concentric Orbit Rings (7 Weekday Circles) -->
''')

for d in range(7):
    r = R_MIN + (d / 6.0) * (R_MAX - R_MIN)
    svg_lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{r:.1f}" fill="none" stroke="{BORDER_MUTED}" stroke-width="1"/>\n')

svg_lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{R_MIN - 12}" fill="none" stroke="{BORDER_DEFAULT}" stroke-width="1"/>\n')

# Expanding Radar Sonar Waves
svg_lines.append(f'''
  <!-- Expanding Radar Wave Pulses -->
  <circle cx="{CX}" cy="{CY}" r="{R_MIN}" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="1" class="wave-1"/>
  <circle cx="{CX}" cy="{CY}" r="{R_MIN}" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="1" class="wave-2"/>
  <circle cx="{CX}" cy="{CY}" r="{R_MIN}" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="1" class="wave-3"/>
''')

# Counter-Rotating Calibrated Perimeter Ring (SMIL Vector Rotation)
svg_lines.append(f'''
  <!-- Calibrated Perimeter Ring with Native SMIL Rotation -->
  <g>
    <circle cx="{CX}" cy="{CY}" r="{R_MAX + 15}" fill="none" stroke="{BORDER_DEFAULT}" stroke-width="1.5" stroke-dasharray="4 6"/>
    <circle cx="{CX}" cy="{CY}" r="{R_MAX + 22}" fill="none" stroke="{BORDER_MUTED}" stroke-width="1" stroke-dasharray="1 8"/>
    <animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="-360 {CX} {CY}" dur="24s" repeatCount="indefinite"/>
  </g>
''')

# Month Spokes & Labels
months = ["AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL"]
for m_idx in range(12):
    angle_deg = m_idx * 30.0 - 90.0
    angle_rad = math.radians(angle_deg)
    x1 = CX + (R_MIN - 12) * math.cos(angle_rad)
    y1 = CY + (R_MIN - 12) * math.sin(angle_rad)
    x2 = CX + (R_MAX + 15) * math.cos(angle_rad)
    y2 = CY + (R_MAX + 15) * math.sin(angle_rad)
    svg_lines.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{BORDER_MUTED}" stroke-width="1"/>\n')
    lx = CX + (R_MAX + 34) * math.cos(angle_rad)
    ly = CY + (R_MAX + 34) * math.sin(angle_rad) + 3.5
    svg_lines.append(f'  <text x="{lx:.1f}" y="{ly:.1f}" fill="{TEXT_MUTED}" font-size="9" font-weight="600" text-anchor="middle" class="code-mono">{months[m_idx]}</text>\n')

deg_labels = [("000°", -90), ("090°", 0), ("180°", 90), ("270°", 180)]
for d_txt, d_ang in deg_labels:
    a_rad = math.radians(d_ang)
    dx = CX + (R_MIN - 24) * math.cos(a_rad)
    dy = CY + (R_MIN - 24) * math.sin(a_rad) + 3
    svg_lines.append(f'  <text x="{dx:.1f}" y="{dy:.1f}" fill="{TEXT_MUTED}" font-size="7.5" font-weight="500" text-anchor="middle" class="code-mono">{d_txt}</text>\n')

svg_lines.append('\n  <!-- 365-Day Polar Contribution Nodes (Strict 4-Tier Rules) -->\n  <g>\n')

# 4-Tier Rules:
# Tier 0 (0 commits): Small resting grid dot (r=1.0, fill=#21262d)
# Tier 1 (1-2 commits): Medium glowing node (r=2.2, fill=#8b949e)
# Tier 2 (3-7 commits): Intense and big radius (r=3.6, fill=#c9d1d9, class="beacon-mid")
# Tier 3 (7+ commits): Very high intensity and large radius (r=5.2, fill=#f0f6fc, class="beacon-high" + flare rays)
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
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="1.0" fill="{BORDER_MUTED}"/>\n')
        elif count <= 2:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="{TEXT_MUTED}"/>\n')
        elif count <= 7:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="3.6" fill="#c9d1d9" class="beacon-mid"/>\n')
        else: # 7+ commits
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="5.2" fill="{TEXT_PRIMARY}" class="beacon-high"/>\n')
            sp_r = R_MAX + 12 + min(count, 50) * 0.5
            sp_x = CX + sp_r * math.cos(angle_rad)
            sp_y = CY + sp_r * math.sin(angle_rad)
            svg_lines.append(f'    <line x1="{px:.1f}" y1="{py:.1f}" x2="{sp_x:.1f}" y2="{sp_y:.1f}" stroke="{TEXT_PRIMARY}" stroke-width="1.5" opacity="0.85"/>\n')
            svg_lines.append(f'    <circle cx="{sp_x:.1f}" cy="{sp_y:.1f}" r="1.8" fill="{TEXT_PRIMARY}"/>\n')

svg_lines.append(f'''  </g>

  <!-- Continuous 360° Rotating Radar Sweep Arm & Phosphor Cone (Native SMIL Transform) -->
  <g>
    <!-- Trailing Phosphor Wedge (60 degrees) -->
    <path d="M {CX} {CY} L {CX - 65} {CY - R_MAX - 15} A {R_MAX + 15} {R_MAX + 15} 0 0 1 {CX} {CY - R_MAX - 15} Z" fill="url(#radarSweepWedge)" opacity="0.85"/>
    
    <!-- Primary Radar Laser Beam Line -->
    <line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R_MAX - 15}" stroke="{TEXT_PRIMARY}" stroke-width="2"/>
    <line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R_MAX - 15}" stroke="{TEXT_PRIMARY}" stroke-width="4" opacity="0.25"/>
    
    <!-- Ion Beam Tip Beacon -->
    <circle cx="{CX}" cy="{CY - R_MAX - 15}" r="3.5" fill="{TEXT_PRIMARY}"/>
    
    <!-- Native Continuous 360-Degree Rotation Animation -->
    <animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" dur="4.2s" repeatCount="indefinite"/>
  </g>

  <!-- Center Radar Hub & Shockwave -->
  <circle cx="{CX}" cy="{CY}" r="4" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="1.5" class="hub-shockwave"/>
  <circle cx="{CX}" cy="{CY}" r="3.5" fill="{TEXT_PRIMARY}"/>
  <line x1="{CX - 10}" y1="{CY}" x2="{CX + 10}" y2="{CY}" stroke="{TEXT_PRIMARY}" stroke-width="1.2"/>
  <line x1="{CX}" y1="{CY - 10}" x2="{CX}" y2="{CY + 10}" stroke="{TEXT_PRIMARY}" stroke-width="1.2"/>

  <!-- Left & Right HUD Panels -->
  <g class="code-mono">
    <rect x="35" y="180" width="135" height="70" rx="4" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
    <text x="45" y="200" fill="{TEXT_MUTED}" font-size="8.5" font-weight="500">// SCAN RANGE</text>
    <text x="45" y="218" fill="{TEXT_PRIMARY}" font-size="13" font-weight="700">360° / 52 WKS</text>
    <text x="45" y="236" fill="{TEXT_MUTED}" font-size="8">RESOLUTION: 7-DAY ORBIT</text>

    <rect x="{WIDTH - 170}" y="180" width="135" height="70" rx="4" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
    <text x="{WIDTH - 160}" y="200" fill="{TEXT_MUTED}" font-size="8.5" font-weight="500">// TOTAL ACTIVITY</text>
    <text x="{WIDTH - 160}" y="218" fill="{TEXT_PRIMARY}" font-size="13" font-weight="700">{total_commits} COMMITS</text>
    <text x="{WIDTH - 160}" y="236" fill="{TEXT_MUTED}" font-size="8">MAX PEAK: 65/DAY</text>
  </g>

  <!-- Footer Bar -->
  <rect x="15" y="{HEIGHT - 32}" width="{WIDTH - 30}" height="22" rx="3" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
  <text x="26" y="{HEIGHT - 17}" fill="{TEXT_MUTED}" font-size="9.5" font-weight="500" class="code-mono">// POLAR TELEMETRY RADAR | ACTIVE VECTOR SWEEP | GITHUB.COM/NAMANINNOVATES</text>
</svg>
''')

target_path = os.path.join(os.path.dirname(__file__), "../assets/radar_sweep.svg")
os.makedirs(os.path.dirname(target_path), exist_ok=True)
with open(target_path, "w") as f:
    f.writelines(svg_lines)

# Also write to legacy path
with open(os.path.join(os.path.dirname(__file__), "../assets/radial_radar.svg"), "w") as f:
    f.writelines(svg_lines)

print("100% Vector Animated SVG Radar generated at:", target_path)
