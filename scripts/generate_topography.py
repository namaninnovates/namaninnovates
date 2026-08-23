import json, math, os
import numpy as np

# Fetch contributions from GitHub GraphQL API via GITHUB_TOKEN or fallback to gh cli / local
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
    print(f"Direct API call failed ({e}), checking local cache...")
    if os.path.exists("/Users/guptanaman/.gemini/antigravity-ide/scratch/contributions.json"):
        with open("/Users/guptanaman/.gemini/antigravity-ide/scratch/contributions.json", "r") as f:
            raw_data = json.load(f)
        cal = raw_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    else:
        raise e

total_commits = cal["totalContributions"]
weeks = cal["weeks"]
num_weeks = len(weeks)

raw_grid = np.zeros((7, num_weeks), dtype=float)
dates_by_week = []
for w_idx, week in enumerate(weeks):
    dates_by_week.append(week["contributionDays"][0]["date"])
    for day in week["contributionDays"]:
        d_idx = day["weekday"]
        raw_grid[d_idx, w_idx] = day["contributionCount"]

grid = np.zeros((7, num_weeks), dtype=float)
for d in range(7):
    src_idx = (d + 1) % 7
    grid[d, :] = raw_grid[src_idx, :]

max_commits = int(np.max(grid))

UP_Y, UP_X = 70, 350
fine_grid = np.zeros((UP_Y, UP_X), dtype=float)

for r in range(UP_Y):
    orig_r = (r / (UP_Y - 1)) * 6.0
    r0 = int(orig_r)
    r1 = min(r0 + 1, 6)
    dr = orig_r - r0
    for c in range(UP_X):
        orig_c = (c / (UP_X - 1)) * (num_weeks - 1)
        c0 = int(orig_c)
        c1 = min(c0 + 1, num_weeks - 1)
        dc = orig_c - c0
        v00 = grid[r0, c0]
        v01 = grid[r0, c1]
        v10 = grid[r1, c0]
        v11 = grid[r1, c1]
        val = (1 - dr) * ((1 - dc) * v00 + dc * v01) + dr * ((1 - dc) * v10 + dc * v11)
        fine_grid[r, c] = val

def gaussian_blur_2d(arr, sigma=2.4):
    k_size = int(math.ceil(sigma * 3)) * 2 + 1
    ax = np.arange(-k_size // 2 + 1.0, k_size // 2 + 1.0)
    kernel_1d = np.exp(-0.5 * (ax / sigma) ** 2)
    kernel_1d /= np.sum(kernel_1d)
    res = np.zeros_like(arr)
    temp = np.zeros_like(arr)
    for r in range(arr.shape[0]):
        temp[r, :] = np.convolve(arr[r, :], kernel_1d, mode="same")
    for c in range(arr.shape[1]):
        res[:, c] = np.convolve(temp[:, c], kernel_1d, mode="same")
    return res

smoothed = gaussian_blur_2d(fine_grid, sigma=3.0)

def marching_squares(field, level):
    segments = []
    rows, cols = field.shape
    for r in range(rows - 1):
        for c in range(cols - 1):
            v0 = field[r, c]
            v1 = field[r, c + 1]
            v2 = field[r + 1, c + 1]
            v3 = field[r + 1, c]
            mask = (1 if v0 >= level else 0) | (2 if v1 >= level else 0) | (4 if v2 >= level else 0) | (8 if v3 >= level else 0)
            if mask == 0 or mask == 15:
                continue
            top_pt = (r, c + (level - v0) / (v1 - v0 + 1e-9))
            right_pt = (r + (level - v1) / (v2 - v1 + 1e-9), c + 1)
            bottom_pt = (r + 1, c + (level - v3) / (v2 - v3 + 1e-9))
            left_pt = (r + (level - v0) / (v3 - v0 + 1e-9), c)
            if mask in (1, 14):   segments.append((left_pt, top_pt))
            elif mask in (2, 13): segments.append((top_pt, right_pt))
            elif mask in (3, 12): segments.append((left_pt, right_pt))
            elif mask in (4, 11): segments.append((right_pt, bottom_pt))
            elif mask in (5, 10):
                segments.append((left_pt, top_pt))
                segments.append((right_pt, bottom_pt))
            elif mask in (6, 9):  segments.append((top_pt, bottom_pt))
            elif mask in (7, 8):  segments.append((left_pt, bottom_pt))
    return segments

def assemble_lines(segments, max_dist=1.5):
    lines = []
    unused = list(segments)
    while unused:
        pt_a, pt_b = unused.pop(0)
        curr_line = [pt_a, pt_b]
        extended = True
        while extended:
            extended = False
            tip = curr_line[-1]
            for idx, (p0, p1) in enumerate(unused):
                d0 = (tip[0] - p0[0]) ** 2 + (tip[1] - p0[1]) ** 2
                d1 = (tip[0] - p1[0]) ** 2 + (tip[1] - p1[1]) ** 2
                if d0 < max_dist ** 2:
                    curr_line.append(p1)
                    unused.pop(idx)
                    extended = True
                    break
                elif d1 < max_dist ** 2:
                    curr_line.append(p0)
                    unused.pop(idx)
                    extended = True
                    break
        lines.append(curr_line)
    return lines

SVG_W, SVG_H = 1000, 320
MAP_X0, MAP_Y0 = 65, 60
MAP_W, MAP_H = 880, 205

levels = [0.8, 2.5, 6.0, 12.0, 22.0, 38.0, 52.0]
level_colors = ["#222222", "#3a3a3a", "#555555", "#777777", "#aaaaaa", "#dddddd", "#ffffff"]
level_widths = [1.0, 1.0, 1.2, 1.2, 1.4, 1.6, 1.8]

svg_lines = []
svg_lines.append(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="100%" height="100%">
  <defs>
    <style>
      .mono {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }}
    </style>
  </defs>

  <!-- Pure Black Background -->
  <rect width="{SVG_W}" height="{SVG_H}" fill="#000000" stroke="#222222" stroke-width="1"/>

  <!-- Inner Frame -->
  <rect x="{MAP_X0}" y="{MAP_Y0}" width="{MAP_W}" height="{MAP_H}" fill="#040404" stroke="#1c1c1c" stroke-width="1"/>

  <!-- Corner Brackets -->
  <path d="M {MAP_X0 + 10} {MAP_Y0} L {MAP_X0} {MAP_Y0} L {MAP_X0} {MAP_Y0 + 10}" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>
  <path d="M {MAP_X0 + MAP_W - 10} {MAP_Y0} L {MAP_X0 + MAP_W} {MAP_Y0} L {MAP_X0 + MAP_W} {MAP_Y0 + 10}" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>
  <path d="M {MAP_X0 + 10} {MAP_Y0 + MAP_H} L {MAP_X0} {MAP_Y0 + MAP_H} L {MAP_X0} {MAP_Y0 + MAP_H - 10}" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>
  <path d="M {MAP_X0 + MAP_W - 10} {MAP_Y0 + MAP_H} L {MAP_X0 + MAP_W} {MAP_Y0 + MAP_H} L {MAP_X0 + MAP_W} {MAP_Y0 + MAP_H - 10}" fill="none" stroke="#FFFFFF" stroke-width="1.5"/>

  <!-- Header -->
  <rect x="15" y="12" width="{SVG_W - 30}" height="32" fill="#000000" stroke="#222222" stroke-width="1"/>
  <text x="28" y="32" fill="#FFFFFF" font-size="12" font-weight="700" class="mono" letter-spacing="1">COMMIT TOPOGRAPHY // ELEVATION CONTOURS</text>
  <text x="{SVG_W - 350}" y="32" fill="#888888" font-size="10" font-weight="600" class="mono">TOTAL: {total_commits} COMMITS | PEAK SPRINT: {max_commits}/DAY</text>

  <!-- Y-Axis Day Labels -->
""")

y_labels = [("MON", 0), ("WED", 2), ("FRI", 4), ("SUN", 6)]
for label, row_idx in y_labels:
    ly = MAP_Y0 + (row_idx + 0.5) / 7.0 * MAP_H + 3
    svg_lines.append(f'  <text x="{MAP_X0 - 10}" y="{ly:.1f}" fill="#666666" font-size="8.5" font-weight="600" text-anchor="end" class="mono">{label}</text>\n')
    gy = MAP_Y0 + (row_idx + 0.5) / 7.0 * MAP_H
    svg_lines.append(f'  <line x1="{MAP_X0}" y1="{gy:.1f}" x2="{MAP_X0 + MAP_W}" y2="{gy:.1f}" stroke="#111111" stroke-width="1" stroke-dasharray="2 4"/>\n')

prev_month = ""
for w_idx in range(num_weeks):
    date_str = dates_by_week[w_idx]
    month_name = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][int(date_str[5:7]) - 1]
    if month_name != prev_month:
        prev_month = month_name
        wx = MAP_X0 + (w_idx / (num_weeks - 1)) * MAP_W
        svg_lines.append(f'  <text x="{wx:.1f}" y="{MAP_Y0 + MAP_H + 16}" fill="#666666" font-size="8.5" font-weight="600" text-anchor="middle" class="mono">{month_name}</text>\n')
        svg_lines.append(f'  <line x1="{wx:.1f}" y1="{MAP_Y0}" x2="{wx:.1f}" y2="{MAP_Y0 + MAP_H}" stroke="#111111" stroke-width="1" stroke-dasharray="2 4"/>\n')

svg_lines.append('\n  <!-- Topographic Elevation Contours -->\n  <g>\n')

for l_idx, level_val in enumerate(levels):
    col = level_colors[min(l_idx, len(level_colors) - 1)]
    lw = level_widths[min(l_idx, len(level_widths) - 1)]
    segs = marching_squares(smoothed, level_val)
    lines = assemble_lines(segs)
    for line in lines:
        if len(line) < 2: continue
        pts = []
        for r, c in line:
            px = MAP_X0 + (c / (UP_X - 1)) * MAP_W
            py = MAP_Y0 + (r / (UP_Y - 1)) * MAP_H
            pts.append(f"{px:.1f},{py:.1f}")
        d_str = "M " + " L ".join(pts)
        svg_lines.append(f'    <path d="{d_str}" fill="none" stroke="{col}" stroke-width="{lw}"/>\n')

svg_lines.append('  </g>\n\n  <!-- Peak Elevation Summit Markers -->\n  <g class="mono">\n')

for r in range(7):
    for c in range(num_weeks):
        val = grid[r, c]
        if val >= 15:
            px = MAP_X0 + (c / (num_weeks - 1)) * MAP_W
            py = MAP_Y0 + ((r + 0.5) / 7.0) * MAP_H
            svg_lines.append(f'''    <circle cx="{px:.1f}" cy="{py:.1f}" r="2" fill="#FFFFFF"/>
    <line x1="{px-4:.1f}" y1="{py:.1f}" x2="{px+4:.1f}" y2="{py:.1f}" stroke="#FFFFFF" stroke-width="1"/>
    <line x1="{px:.1f}" y1="{py-4:.1f}" x2="{px:.1f}" y2="{py+4:.1f}" stroke="#FFFFFF" stroke-width="1"/>
''')
            if val >= 25:
                svg_lines.append(f'    <text x="{px+5:.1f}" y="{py-4:.1f}" fill="#FFFFFF" font-size="8" font-weight="700">▲{int(val)}</text>\n')

svg_lines.append(f"""  </g>

  <!-- Footer Bar -->
  <rect x="15" y="{SVG_H - 32}" width="{SVG_W - 30}" height="22" fill="#000000" stroke="#222222" stroke-width="1"/>
  <text x="26" y="{SVG_H - 17}" fill="#888888" font-size="9.5" font-weight="600" class="mono">// 52-WEEK COMMIT ELEVATION | ISO-INTERVAL: 5 COMMITS | GITHUB.COM/NAMANINNOVATES</text>
</svg>
""")

target_path = os.path.join(os.path.dirname(__file__), "../assets/topographic_heatmap.svg")
os.makedirs(os.path.dirname(target_path), exist_ok=True)
with open(target_path, "w") as f:
    f.writelines(svg_lines)

print("Topographic Heatmap SVG updated successfully at:", target_path)
