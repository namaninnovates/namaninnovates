import json, math, os

data_path = os.path.join(os.path.dirname(__file__), 'land_points.json')
with open(data_path, 'r') as f:
    land_points = json.load(f)

WIDTH, HEIGHT = 1000, 520
MAP_X0, MAP_Y0 = 35, 55
MAP_W, MAP_H = 930, 415

def latlon_to_xy(lat, lon):
    lat_min, lat_max = -58.0, 75.0
    lon_min, lon_max = -170.0, 180.0
    x = MAP_X0 + (lon - lon_min) / (lon_max - lon_min) * MAP_W
    y = MAP_Y0 + (lat_max - lat) / (lat_max - lat_min) * MAP_H
    return round(x, 1), round(y, 1)

LOCATIONS = [
    {"name": "CHANDIGARH",    "lat": 30.7333, "lon":  76.7794, "id": "01", "dir": (-76, -42)},
    {"name": "NEW DELHI",     "lat": 28.6139, "lon":  77.2090, "id": "02", "dir": (-76, -20)},
    {"name": "MUMBAI",        "lat": 19.0760, "lon":  72.8777, "id": "03", "dir": (-86, 14)},
    {"name": "BANGALORE",     "lat": 12.9716, "lon":  77.5946, "id": "04", "dir": (-95, 26)},
    {"name": "HYDERABAD",     "lat": 17.3850, "lon":  78.4867, "id": "05", "dir": (-20, 54)},
    {"name": "CHENNAI",       "lat": 13.0827, "lon":  80.2707, "id": "06", "dir": (78, 38)},
    {"name": "KOLKATA",       "lat": 22.5726, "lon":  88.3639, "id": "07", "dir": (78, 12)},
    {"name": "BHOPAL",        "lat": 23.2599, "lon":  77.4126, "id": "08", "dir": (0, -32)},
    {"name": "VELLORE",       "lat": 12.9165, "lon":  79.1325, "id": "09", "dir": (35, 74)},
    {"name": "TRIPURA",       "lat": 23.8315, "lon":  91.2868, "id": "10", "dir": (78, -16)},
    {"name": "SURAT",         "lat": 21.1702, "lon":  72.8311, "id": "11", "dir": (-80, -4)},
    {"name": "LONDON [UK]",   "lat": 51.5074, "lon":  -0.1278, "id": "12", "dir": (-68, -34)},
    {"name": "GERMANY [EU]",  "lat": 51.1657, "lon":  10.4515, "id": "13", "dir": (22, -34)},
    {"name": "FLORIDA [USA]", "lat": 27.6648, "lon": -81.5158, "id": "14", "dir": (-75, -28)},
    {"name": "MIAMI [USA]",   "lat": 25.7617, "lon": -80.1918, "id": "15", "dir": (-75, 16)},
]

ARCS = [
    (0, 11, -55), # Chandigarh -> London
    (0, 12, -45), # Chandigarh -> Germany
    (0, 13, -78), # Chandigarh -> Florida
    (0, 1,  -8),  # Chandigarh -> New Delhi
    (0, 7,  -14), # Chandigarh -> Bhopal
    (1, 10, -10), # New Delhi -> Surat
    (10, 2,  6),  # Surat -> Mumbai
    (7, 3,  -14), # Bhopal -> Bangalore
    (2, 6,  -14), # Mumbai -> Kolkata
    (5, 8,  8),   # Chennai -> Vellore
    (7, 4,  -10), # Bhopal -> Hyderabad
    (9, 6,  -10), # Tripura -> Kolkata
    (11, 13, -40),# London -> Florida
    (13, 14, 6),  # Florida -> Miami
]

PANEL_BG = "#161b22"
BORDER_DEFAULT = "#30363d"
BORDER_MUTED = "#21262d"
TEXT_PRIMARY = "#f0f6fc"
TEXT_MUTED = "#8b949e"
LAND_DOT_COLOR = "#8b949e"

svg_lines = []
svg_lines.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%">
  <defs>
    <style>
      @keyframes pulseRing {{
        0% {{ r: 3; stroke-opacity: 0.9; }}
        100% {{ r: 15; stroke-opacity: 0; }}
      }}
      @keyframes flowPacket {{
        0% {{ stroke-dashoffset: 75; }}
        100% {{ stroke-dashoffset: 0; }}
      }}
      .pulse-1 {{ animation: pulseRing 2.6s cubic-bezier(0.2, 0.8, 0.2, 1) infinite; }}
      .pulse-2 {{ animation: pulseRing 2.6s cubic-bezier(0.2, 0.8, 0.2, 1) infinite 0.85s; }}
      .pulse-3 {{ animation: pulseRing 2.6s cubic-bezier(0.2, 0.8, 0.2, 1) infinite 1.7s; }}
      .flow-arc {{
        stroke-dasharray: 10 65;
        animation: flowPacket 3.2s linear infinite;
      }}
      .code-mono {{
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }}
    </style>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" rx="6" fill="none" stroke="{BORDER_DEFAULT}" stroke-width="1"/>

  <!-- Faint Coordinate Grid Lines -->
''')

for x in range(MAP_X0, MAP_X0 + MAP_W + 1, 62):
    svg_lines.append(f'  <line x1="{x}" y1="{MAP_Y0}" x2="{x}" y2="{MAP_Y0 + MAP_H}" stroke="{BORDER_MUTED}" stroke-width="1" opacity="0.5"/>\n')
for y in range(MAP_Y0, MAP_Y0 + MAP_H + 1, 44):
    svg_lines.append(f'  <line x1="{MAP_X0}" y1="{y}" x2="{MAP_X0 + MAP_W}" y2="{y}" stroke="{BORDER_MUTED}" stroke-width="1" opacity="0.5"/>\n')

eq_y = latlon_to_xy(0, 0)[1]
pm_x = latlon_to_xy(0, 0)[0]
svg_lines.append(f'  <line x1="{MAP_X0}" y1="{eq_y}" x2="{MAP_X0 + MAP_W}" y2="{eq_y}" stroke="{BORDER_DEFAULT}" stroke-width="1" stroke-dasharray="4 4"/>\n')
svg_lines.append(f'  <line x1="{pm_x}" y1="{MAP_Y0}" x2="{pm_x}" y2="{MAP_Y0 + MAP_H}" stroke="{BORDER_DEFAULT}" stroke-width="1" stroke-dasharray="4 4"/>\n')

svg_lines.append(f'  <rect x="{MAP_X0}" y="{MAP_Y0}" width="{MAP_W}" height="{MAP_H}" fill="none" stroke="{BORDER_MUTED}" stroke-width="1"/>\n')

svg_lines.append(f'''
  <!-- Header Bar -->
  <rect x="15" y="12" width="{WIDTH - 30}" height="32" rx="4" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
  <text x="28" y="32" fill="{TEXT_PRIMARY}" font-size="12" font-weight="600" class="code-mono" letter-spacing="0.5">GLOBAL CLIENT NETWORK // 15 HUBS</text>
  <text x="{WIDTH - 145}" y="32" fill="{TEXT_MUTED}" font-size="10" font-weight="500" class="code-mono">[NAMAN GUPTA]</text>

  <!-- High-Visibility Landmass Points -->
  <g fill="{LAND_DOT_COLOR}" opacity="0.75">
''')

for lat, lon in land_points:
    if -58 <= lat <= 75 and -170 <= lon <= 180:
        px, py = latlon_to_xy(lat, lon)
        svg_lines.append(f'    <circle cx="{px}" cy="{py}" r="1.3"/>\n')

svg_lines.append('  </g>\n\n  <!-- Transit Arcs -->\n  <g>\n')

for idx0, idx1, curve_h in ARCS:
    p0 = latlon_to_xy(LOCATIONS[idx0]["lat"], LOCATIONS[idx0]["lon"])
    p1 = latlon_to_xy(LOCATIONS[idx1]["lat"], LOCATIONS[idx1]["lon"])
    mx = round((p0[0] + p1[0]) / 2.0, 1)
    my = round((p0[1] + p1[1]) / 2.0 + curve_h, 1)
    
    path_d = f"M {p0[0]} {p0[1]} Q {mx} {my} {p1[0]} {p1[1]}"
    svg_lines.append(f'    <path d="{path_d}" fill="none" stroke="{BORDER_DEFAULT}" stroke-width="1.2" opacity="0.7"/>\n')
    svg_lines.append(f'    <path d="{path_d}" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="1.8" class="flow-arc"/>\n')

svg_lines.append('  </g>\n\n  <!-- Location Beacons & Callouts -->\n  <g class="code-mono">\n')

for i, loc in enumerate(LOCATIONS):
    nx, ny = latlon_to_xy(loc["lat"], loc["lon"])
    dx, dy = loc["dir"]
    tx = round(nx + dx, 1)
    ty = round(ny + dy, 1)
    
    pulse_cls = f"pulse-{(i % 3) + 1}"
    svg_lines.append(f'''    <!-- Node {loc["id"]}: {loc["name"]} -->
    <circle cx="{nx}" cy="{ny}" r="3.5" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="1" class="{pulse_cls}"/>
    <line x1="{nx - 4}" y1="{ny}" x2="{nx + 4}" y2="{ny}" stroke="{TEXT_MUTED}" stroke-width="1"/>
    <line x1="{nx}" y1="{ny - 4}" x2="{nx}" y2="{ny + 4}" stroke="{TEXT_MUTED}" stroke-width="1"/>
    <circle cx="{nx}" cy="{ny}" r="2.2" fill="{TEXT_PRIMARY}"/>
''')
    svg_lines.append(f'    <line x1="{nx}" y1="{ny}" x2="{tx}" y2="{ty}" stroke="{BORDER_DEFAULT}" stroke-width="1.2"/>\n')
    
    label_txt = f"{loc['id']}::{loc['name']}"
    badge_w = len(label_txt) * 7.0 + 8
    bx = tx if dx >= 0 else round(tx - badge_w, 1)
    by = round(ty - 7, 1)
    
    svg_lines.append(f'    <rect x="{bx}" y="{by}" width="{badge_w}" height="14" rx="3" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>\n')
    svg_lines.append(f'    <text x="{bx + 4}" y="{by + 10.5}" fill="{TEXT_PRIMARY}" font-size="8.5" font-weight="600">{label_txt}</text>\n\n')

svg_lines.append(f'''  </g>

  <!-- Footer Bar -->
  <rect x="15" y="{HEIGHT - 32}" width="{WIDTH - 30}" height="22" rx="3" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
  <text x="26" y="{HEIGHT - 17}" fill="{TEXT_MUTED}" font-size="9.5" font-weight="500" class="code-mono">// 01: CHANDIGARH [30.73°N 76.78°E] | 15 GLOBAL HUBS | GITHUB.COM/NAMANINNOVATES</text>
</svg>
''')

target_path = os.path.join(os.path.dirname(__file__), '../assets/client_topology.svg')
os.makedirs(os.path.dirname(target_path), exist_ok=True)
with open(target_path, 'w') as f:
    f.writelines(svg_lines)

# Also write to legacy path
with open(os.path.join(os.path.dirname(__file__), '../assets/global_telemetry_map.svg'), 'w') as f:
    f.writelines(svg_lines)

print("World Map SVG successfully updated with Florida, London, Surat (15 hubs total)!")
