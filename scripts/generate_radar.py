import json, math, os, subprocess, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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
    fallback_file = os.path.join(os.path.dirname(__file__), "contributions.json")
    with open(fallback_file, "r") as f:
        raw_data = json.load(f)
    cal = raw_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

total_commits = cal["totalContributions"]
weeks = cal["weeks"]
num_weeks = len(weeks)

WIDTH, HEIGHT = 1000, 520
CX, CY = 500, 270
R_MIN = 60
R_MAX = 195

BG_RGB = (13, 17, 23)           # #0d1117 (Solid opaque background)
PANEL_RGB = (22, 27, 34)        # #161b22
BORDER_DEFAULT = (48, 54, 61)   # #30363d
BORDER_MUTED = (33, 38, 45)     # #21262d
TEXT_PRIMARY = (240, 246, 252)  # #f0f6fc
TEXT_MUTED = (139, 148, 158)    # #8b949e

try:
    font_mono_xs = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 9)
    font_mono_sm = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 11)
    font_mono_lg = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 13)
except Exception:
    font_mono_xs = ImageFont.load_default()
    font_mono_sm = ImageFont.load_default()
    font_mono_lg = ImageFont.load_default()

day_nodes = []
for w_idx, week in enumerate(weeks):
    frac_w = w_idx / float(num_weeks)
    angle_deg = frac_w * 360.0
    angle_rad = math.radians(angle_deg - 90.0)
    
    for day in week["contributionDays"]:
        count = day["contributionCount"]
        d_idx = (day["weekday"] + 6) % 7
        r = R_MIN + (d_idx / 6.0) * (R_MAX - R_MIN)
        day_nodes.append({
            "x": CX + r * math.cos(angle_rad),
            "y": CY + r * math.sin(angle_rad),
            "r": r,
            "angle_deg": angle_deg,
            "angle_rad": angle_rad,
            "count": count
        })

frames_dir = os.path.join(os.path.dirname(__file__), "../assets/radar_temp_frames")
if os.path.exists(frames_dir):
    shutil.rmtree(frames_dir)
os.makedirs(frames_dir, exist_ok=True)

TOTAL_FRAMES = 96
SWEEP_TRAIL_DEG = 120.0
months = ["AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL"]

print(f"Rendering {TOTAL_FRAMES} radar frames with {total_commits} contributions...")

for frame_idx in range(TOTAL_FRAMES):
    sweep_angle_deg = (frame_idx / float(TOTAL_FRAMES)) * 360.0
    sweep_angle_rad = math.radians(sweep_angle_deg - 90.0)
    
    img = Image.new("RGBA", (WIDTH, HEIGHT), (*BG_RGB, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer Border
    draw.rounded_rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], radius=6, outline=(*BORDER_DEFAULT, 255), width=1)
    
    # Header Bar
    draw.rounded_rectangle([(15, 12), (WIDTH - 15, 44)], radius=4, fill=(*PANEL_RGB, 255), outline=(*BORDER_DEFAULT, 255), width=1)
    draw.text((28, 22), "RADIAL RADAR TELEMETRY // 360° PPI SCANNER", font=font_mono_sm, fill=(*TEXT_PRIMARY, 255))
    draw.text((WIDTH - 325, 22), f"TOTAL: {total_commits} COMMITS | 52 WEEKS ACTIVE", font=font_mono_xs, fill=(*TEXT_MUTED, 255))
    
    # Concentric Weekday Rings
    for d in range(7):
        r = R_MIN + (d / 6.0) * (R_MAX - R_MIN)
        draw.ellipse([(CX - r, CY - r), (CX + r, CY + r)], outline=(*BORDER_MUTED, 255), width=1)
        
    draw.ellipse([(CX - (R_MAX + 15), CY - (R_MAX + 15)), (CX + (R_MAX + 15), CY + (R_MAX + 15))], outline=(*BORDER_DEFAULT, 255), width=1)
    draw.ellipse([(CX - (R_MIN - 12), CY - (R_MIN - 12)), (CX + (R_MIN - 12), CY + (R_MIN - 12))], outline=(*BORDER_DEFAULT, 255), width=1)
    
    # Month Spokes & Labels
    for m_idx in range(12):
        a_deg = m_idx * 30.0
        a_rad = math.radians(a_deg - 90.0)
        x1 = CX + (R_MIN - 12) * math.cos(a_rad)
        y1 = CY + (R_MIN - 12) * math.sin(a_rad)
        x2 = CX + (R_MAX + 15) * math.cos(a_rad)
        y2 = CY + (R_MAX + 15) * math.sin(a_rad)
        draw.line([(x1, y1), (x2, y2)], fill=(*BORDER_MUTED, 255), width=1)
        
        lx = CX + (R_MAX + 28) * math.cos(a_rad)
        ly = CY + (R_MAX + 28) * math.sin(a_rad) - 5
        draw.text((lx - 8, ly), months[m_idx], font=font_mono_xs, fill=(*TEXT_MUTED, 255))

    # Dormant Nodes (Tiny subtle resting dots in background)
    for node in day_nodes:
        ang = node["angle_deg"]
        diff = (sweep_angle_deg - ang) % 360.0
        if diff >= SWEEP_TRAIL_DEG:
            nx, ny = node["x"], node["y"]
            draw.ellipse([(nx - 0.9, ny - 0.9), (nx + 0.9, ny + 0.9)], fill=(24, 28, 35, 255))

    # Phosphor Sweep Sector Wedge
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    
    steps = 45
    for s in range(steps):
        frac = s / float(steps)
        t_deg = (sweep_angle_deg - (1.0 - frac) * SWEEP_TRAIL_DEG) % 360.0
        t_rad = math.radians(t_deg - 90.0)
        t_deg_next = (sweep_angle_deg - (1.0 - (s + 1) / float(steps)) * SWEEP_TRAIL_DEG) % 360.0
        t_rad_next = math.radians(t_deg_next - 90.0)
        
        alpha = int(52 * (frac ** 2.0))
        p1 = (CX + (R_MIN - 10) * math.cos(t_rad), CY + (R_MIN - 10) * math.sin(t_rad))
        p2 = (CX + (R_MAX + 15) * math.cos(t_rad), CY + (R_MAX + 15) * math.sin(t_rad))
        p3 = (CX + (R_MAX + 15) * math.cos(t_rad_next), CY + (R_MAX + 15) * math.sin(t_rad_next))
        p4 = (CX + (R_MIN - 10) * math.cos(t_rad_next), CY + (R_MIN - 10) * math.sin(t_rad_next))
        ov_draw.polygon([p1, p2, p3, p4], fill=(240, 246, 252, alpha))
        
    # Primary Radar Laser Beam Line
    beam_x = CX + (R_MAX + 15) * math.cos(sweep_angle_rad)
    beam_y = CY + (R_MAX + 15) * math.sin(sweep_angle_rad)
    ov_draw.line([(CX, CY), (beam_x, beam_y)], fill=(255, 255, 255, 245), width=2)
    
    # Active Nodes (Ignite in real time under beam sweep)
    for node in day_nodes:
        ang = node["angle_deg"]
        diff = (sweep_angle_deg - ang) % 360.0
        if diff < SWEEP_TRAIL_DEG:
            decay = ((SWEEP_TRAIL_DEG - diff) / SWEEP_TRAIL_DEG) ** 1.3
            count = node["count"]
            nx, ny = node["x"], node["y"]
            
            if count == 0:
                v = int(24 + (75 - 24) * decay)
                ov_draw.ellipse([(nx - 1.0, ny - 1.0), (nx + 1.0, ny + 1.0)], fill=(v, v, v, 255))
            elif count <= 2:
                radius = 1.6 + 1.4 * decay
                r_c = int(50 + 190 * decay)
                g_c = int(60 + 190 * decay)
                b_c = int(75 + 180 * decay)
                ov_draw.ellipse([(nx - radius, ny - radius), (nx + radius, ny + radius)], fill=(r_c, g_c, b_c, 255))
            elif count <= 7:
                radius = 2.4 + 2.8 * decay
                r_c = int(90 + 165 * decay)
                g_c = int(105 + 150 * decay)
                b_c = int(130 + 125 * decay)
                ov_draw.ellipse([(nx - radius, ny - radius), (nx + radius, ny + radius)], fill=(r_c, g_c, b_c, 255))
                if decay > 0.35:
                    ov_draw.ellipse([(nx - (radius + 1.5), ny - (radius + 1.5)), (nx + (radius + 1.5), ny + (radius + 1.5))], outline=(240, 246, 252, int(140 * decay)), width=1)
            else: # 7+ Commits
                radius = 3.4 + 4.2 * decay
                ov_draw.ellipse([(nx - radius, ny - radius), (nx + radius, ny + radius)], fill=(255, 255, 255, 255))
                if decay > 0.25:
                    ring_r = radius + 2.4 * decay
                    ov_draw.ellipse([(nx - ring_r, ny - ring_r), (nx + ring_r, ny + ring_r)], outline=(255, 255, 255, int(210 * decay)), width=1)

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Center Hub Pulse
    hub_phase = (frame_idx / float(TOTAL_FRAMES) * 2.0) % 1.0
    hub_r = 4 + hub_phase * 18
    hub_alpha = int(180 * (1.0 - hub_phase))
    draw.ellipse([(CX - hub_r, CY - hub_r), (CX + hub_r, CY + hub_r)], outline=(240, 246, 252, hub_alpha), width=1)
    draw.ellipse([(CX - 3, CY - 3), (CX + 3, CY + 3)], fill=(*TEXT_PRIMARY, 255))
    draw.line([(CX - 8, CY), (CX + 8, CY)], fill=(*TEXT_PRIMARY, 255), width=1)
    draw.line([(CX, CY - 8), (CX, CY + 8)], fill=(*TEXT_PRIMARY, 255), width=1)

    # Left & Right HUD Panels
    draw.rounded_rectangle([(35, 180), (170, 250)], radius=4, fill=(*PANEL_RGB, 255), outline=(*BORDER_DEFAULT, 255), width=1)
    draw.text((45, 192), "// SCAN BEARING", font=font_mono_xs, fill=(*TEXT_MUTED, 255))
    draw.text((45, 210), f"{int(sweep_angle_deg):03d}° PPI", font=font_mono_lg, fill=(*TEXT_PRIMARY, 255))
    draw.text((45, 230), "STATUS: SCANNING", font=font_mono_xs, fill=(*TEXT_MUTED, 255))

    draw.rounded_rectangle([(WIDTH - 170, 180), (WIDTH - 35, 250)], radius=4, fill=(*PANEL_RGB, 255), outline=(*BORDER_DEFAULT, 255), width=1)
    draw.text((WIDTH - 160, 192), "// TOTAL COMMITS", font=font_mono_xs, fill=(*TEXT_MUTED, 255))
    draw.text((WIDTH - 160, 210), f"{total_commits} EVENTS", font=font_mono_lg, fill=(*TEXT_PRIMARY, 255))
    draw.text((WIDTH - 160, 230), "MAX PEAK: 65/DAY", font=font_mono_xs, fill=(*TEXT_MUTED, 255))

    # Footer Bar
    draw.rounded_rectangle([(15, HEIGHT - 34), (WIDTH - 15, HEIGHT - 12)], radius=3, fill=(*PANEL_RGB, 255), outline=(*BORDER_DEFAULT, 255), width=1)
    draw.text((26, HEIGHT - 23), "// 360° SYNCHRONIZED RADAR | RANGE: 52 WEEKS | GITHUB.COM/NAMANINNOVATES", font=font_mono_xs, fill=(*TEXT_MUTED, 255))

    rgb_img = img.convert("RGB")
    rgb_img.save(f"{frames_dir}/frame_{frame_idx:03d}.png")

target_gif_fresh = os.path.join(os.path.dirname(__file__), "../assets/radar_telemetry_ppi.gif")
target_gif_scope = os.path.join(os.path.dirname(__file__), "../assets/radial_radar_scope.gif")
target_gif_legacy = os.path.join(os.path.dirname(__file__), "../assets/radial_radar.gif")
ffmpeg_bin = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"

subprocess.run([
    ffmpeg_bin, "-y", "-r", "20",
    "-i", f"{frames_dir}/frame_%03d.png",
    "-vf", "fps=20,scale=1000:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=full[p];[s1][p]paletteuse=dither=bayer:bayer_scale=1:diff_mode=none",
    target_gif_fresh
], check=True)

shutil.copyfile(target_gif_fresh, target_gif_scope)
shutil.copyfile(target_gif_fresh, target_gif_legacy)
shutil.rmtree(frames_dir)
print("Radar GIF compiled successfully with total:", total_commits)

# Also generate clean vector SVG Radar
svg_lines = []
svg_lines.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%">
  <defs>
    <style>
      .code-mono {{
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }}
      @keyframes pulseSonarWave {{
        0% {{ r: {R_MIN}px; stroke-opacity: 0.85; }}
        100% {{ r: {R_MAX + 16}px; stroke-opacity: 0; }}
      }}
      @keyframes beaconGlow {{
        0%, 100% {{ r: 5.4px; fill-opacity: 0.9; }}
        50% {{ r: 6.8px; fill-opacity: 1; }}
      }}
      @keyframes midGlow {{
        0%, 100% {{ r: 3.6px; fill-opacity: 0.8; }}
        50% {{ r: 4.6px; fill-opacity: 1; }}
      }}
      @keyframes hubShockwave {{
        0% {{ r: 4px; stroke-opacity: 0.9; }}
        100% {{ r: 30px; stroke-opacity: 0; }}
      }}
      .sonar-1 {{ animation: pulseSonarWave 3.6s cubic-bezier(0.1, 0.8, 0.2, 1) infinite; }}
      .sonar-2 {{ animation: pulseSonarWave 3.6s cubic-bezier(0.1, 0.8, 0.2, 1) infinite 1.2s; }}
      .sonar-3 {{ animation: pulseSonarWave 3.6s cubic-bezier(0.1, 0.8, 0.2, 1) infinite 2.4s; }}
      .hub-wave {{ animation: hubShockwave 2.2s cubic-bezier(0.2, 0.8, 0.2, 1) infinite; }}
      .beacon-high {{ animation: beaconGlow 2.2s ease-in-out infinite; }}
      .beacon-mid {{ animation: midGlow 3s ease-in-out infinite; }}
    </style>
    <radialGradient id="radarSweepGradient" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#f0f6fc" stop-opacity="0.30"/>
      <stop offset="60%" stop-color="#f0f6fc" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#f0f6fc" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" rx="6" fill="none" stroke="#30363d" stroke-width="1"/>

  <!-- Header Bar -->
  <rect x="15" y="12" width="{WIDTH - 30}" height="32" rx="4" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <text x="28" y="32" fill="#f0f6fc" font-size="12" font-weight="600" class="code-mono" letter-spacing="0.5">RADIAL CONTRIBUTION RADAR // 360° POLAR TELEMETRY</text>
  <text x="{WIDTH - 325}" y="32" fill="#8b949e" font-size="10" font-weight="500" class="code-mono">TOTAL: {total_commits} COMMITS | 52 WEEKS ACTIVE</text>

  <!-- 7 Concentric Weekday Orbits -->
''')

for d in range(7):
    r = R_MIN + (d / 6.0) * (R_MAX - R_MIN)
    svg_lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{r:.1f}" fill="none" stroke="#21262d" stroke-width="1"/>\n')

svg_lines.append(f'  <circle cx="{CX}" cy="{CY}" r="{R_MIN - 12}" fill="none" stroke="#30363d" stroke-width="1"/>\n')

svg_lines.append(f'''
  <!-- Expanding Sonar Waves -->
  <circle cx="{CX}" cy="{CY}" r="{R_MIN}" fill="none" stroke="#f0f6fc" stroke-width="1" class="sonar-1"/>
  <circle cx="{CX}" cy="{CY}" r="{R_MIN}" fill="none" stroke="#f0f6fc" stroke-width="1" class="sonar-2"/>
  <circle cx="{CX}" cy="{CY}" r="{R_MIN}" fill="none" stroke="#f0f6fc" stroke-width="1" class="sonar-3"/>
''')

svg_lines.append(f'''
  <!-- Calibrated Perimeter Reticle -->
  <g>
    <circle cx="{CX}" cy="{CY}" r="{R_MAX + 15}" fill="none" stroke="#30363d" stroke-width="1.5" stroke-dasharray="4 6"/>
    <circle cx="{CX}" cy="{CY}" r="{R_MAX + 22}" fill="none" stroke="#21262d" stroke-width="1" stroke-dasharray="1 8"/>
    <animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="-360 {CX} {CY}" dur="24s" repeatCount="indefinite"/>
  </g>
''')

for m_idx in range(12):
    angle_deg = m_idx * 30.0 - 90.0
    angle_rad = math.radians(angle_deg)
    x1 = CX + (R_MIN - 12) * math.cos(angle_rad)
    y1 = CY + (R_MIN - 12) * math.sin(angle_rad)
    x2 = CX + (R_MAX + 15) * math.cos(angle_rad)
    y2 = CY + (R_MAX + 15) * math.sin(angle_rad)
    svg_lines.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#21262d" stroke-width="1"/>\n')
    lx = CX + (R_MAX + 34) * math.cos(angle_rad)
    ly = CY + (R_MAX + 34) * math.sin(angle_rad) + 3.5
    svg_lines.append(f'  <text x="{lx:.1f}" y="{ly:.1f}" fill="#8b949e" font-size="9" font-weight="600" text-anchor="middle" class="code-mono">{months[m_idx]}</text>\n')

deg_labels = [("000°", -90), ("090°", 0), ("180°", 90), ("270°", 180)]
for d_txt, d_ang in deg_labels:
    a_rad = math.radians(d_ang)
    dx = CX + (R_MIN - 24) * math.cos(a_rad)
    dy = CY + (R_MIN - 24) * math.sin(a_rad) + 3
    svg_lines.append(f'  <text x="{dx:.1f}" y="{dy:.1f}" fill="#8b949e" font-size="7.5" font-weight="500" text-anchor="middle" class="code-mono">{d_txt}</text>\n')

svg_lines.append('\n  <!-- 365-Day Polar Contribution Nodes -->\n  <g>\n')

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
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="1.0" fill="#21262d"/>\n')
        elif count <= 2:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="#8b949e"/>\n')
        elif count <= 7:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="3.6" fill="#c9d1d9" class="beacon-mid"/>\n')
        else:
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="7.5" fill="none" stroke="#f0f6fc" stroke-width="1" opacity="0.4"/>\n')
            svg_lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="5.4" fill="#f0f6fc" class="beacon-high"/>\n')

svg_lines.append(f'''  </g>

  <!-- 360° Rotating Radar Sweep Arm & Trailing Phosphor Wedge -->
  <g>
    <path d="M {CX} {CY} L {CX - 65} {CY - R_MAX - 15} A {R_MAX + 15} {R_MAX + 15} 0 0 1 {CX} {CY - R_MAX - 15} Z" fill="url(#radarSweepGradient)" opacity="0.85"/>
    <line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R_MAX - 15}" stroke="#f0f6fc" stroke-width="2"/>
    <line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R_MAX - 15}" stroke="#f0f6fc" stroke-width="4" opacity="0.25"/>
    <circle cx="{CX}" cy="{CY - R_MAX - 15}" r="3.5" fill="#f0f6fc"/>
    <animateTransform attributeName="transform" type="rotate" from="0 {CX} {CY}" to="360 {CX} {CY}" dur="4.8s" repeatCount="indefinite"/>
  </g>

  <!-- Center Hub -->
  <circle cx="{CX}" cy="{CY}" r="4" fill="none" stroke="#f0f6fc" stroke-width="1.5" class="hub-wave"/>
  <circle cx="{CX}" cy="{CY}" r="3.5" fill="#f0f6fc"/>
  <line x1="{CX - 10}" y1="{CY}" x2="{CX + 10}" y2="{CY}" stroke="#f0f6fc" stroke-width="1.2"/>
  <line x1="{CX}" y1="{CY - 10}" x2="{CX}" y2="{CY + 10}" stroke="#f0f6fc" stroke-width="1.2"/>

  <!-- Left & Right HUD Panels -->
  <g class="code-mono">
    <rect x="35" y="180" width="135" height="70" rx="4" fill="#161b22" stroke="#30363d" stroke-width="1"/>
    <text x="45" y="200" fill="#8b949e" font-size="8.5" font-weight="500">// SCAN RANGE</text>
    <text x="45" y="218" fill="#f0f6fc" font-size="13" font-weight="700">360° / 52 WKS</text>
    <text x="45" y="236" fill="#8b949e" font-size="8">RESOLUTION: 7-DAY ORBIT</text>

    <rect x="{WIDTH - 170}" y="180" width="135" height="70" rx="4" fill="#161b22" stroke="#30363d" stroke-width="1"/>
    <text x="{WIDTH - 160}" y="200" fill="#8b949e" font-size="8.5" font-weight="500">// TOTAL ACTIVITY</text>
    <text x="{WIDTH - 160}" y="218" fill="#f0f6fc" font-size="13" font-weight="700">{total_commits} COMMITS</text>
    <text x="{WIDTH - 160}" y="236" fill="#8b949e" font-size="8">MAX PEAK: 65/DAY</text>
  </g>

  <!-- Footer Bar -->
  <rect x="15" y="{HEIGHT - 32}" width="{WIDTH - 30}" height="22" rx="3" fill="#161b22" stroke="#30363d" stroke-width="1"/>
  <text x="26" y="{HEIGHT - 17}" fill="#8b949e" font-size="9.5" font-weight="500" class="code-mono">// POLAR CONTRIBUTION RADAR | 360° VECTOR TELEMETRY | GITHUB.COM/NAMANINNOVATES</text>
</svg>
''')

target_svg = os.path.join(os.path.dirname(__file__), "../assets/radar_telemetry.svg")
target_radial_svg = os.path.join(os.path.dirname(__file__), "../assets/radial_radar.svg")
target_heatmap_svg = os.path.join(os.path.dirname(__file__), "../assets/radial_radar_heatmap.svg")
with open(target_svg, "w") as f:
    f.writelines(svg_lines)
with open(target_radial_svg, "w") as f:
    f.writelines(svg_lines)
with open(target_heatmap_svg, "w") as f:
    f.writelines(svg_lines)

print("Vector SVG Radar generated with live total:", total_commits)
