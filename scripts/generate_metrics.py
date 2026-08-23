import json, os

WIDTH, HEIGHT = 1000, 175
PANEL_BG = "#161b22"
BORDER_DEFAULT = "#30363d"
BORDER_MUTED = "#21262d"
TEXT_PRIMARY = "#f0f6fc"
TEXT_MUTED = "#8b949e"

LANGS = [
    ("Python", 88.57, "#f0f6fc"),
    ("JavaScript", 7.47, "#c9d1d9"),
    ("HTML", 1.73, "#8b949e"),
    ("TypeScript", 1.47, "#6e7681"),
    ("C / Other", 0.76, "#30363d"),
]

svg_lines = []
svg_lines.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%">
  <defs>
    <style>
      .code-mono {{
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }}
    </style>
  </defs>

  <rect width="{WIDTH}" height="{HEIGHT}" rx="6" fill="none" stroke="{BORDER_DEFAULT}" stroke-width="1"/>

  <!-- Card 1: Stats -->
  <g class="code-mono">
    <rect x="15" y="15" width="310" height="{HEIGHT - 30}" rx="5" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
    <text x="30" y="42" fill="{TEXT_PRIMARY}" font-size="12" font-weight="700">GITHUB STATS</text>
    <line x1="30" y1="52" x2="310" y2="52" stroke="{BORDER_MUTED}" stroke-width="1"/>
    
    <text x="30" y="80" fill="{TEXT_MUTED}" font-size="10.5">Total Commits:</text>
    <text x="305" y="80" fill="{TEXT_PRIMARY}" font-size="11.5" font-weight="700" text-anchor="end">580</text>
    
    <text x="30" y="108" fill="{TEXT_MUTED}" font-size="10.5">Repositories:</text>
    <text x="305" y="108" fill="{TEXT_PRIMARY}" font-size="11.5" font-weight="700" text-anchor="end">12</text>
    
    <text x="30" y="136" fill="{TEXT_MUTED}" font-size="10.5">Stars Earned:</text>
    <text x="305" y="136" fill="{TEXT_PRIMARY}" font-size="11.5" font-weight="700" text-anchor="end">1</text>
  </g>

  <!-- Card 2: Languages -->
  <g class="code-mono">
    <rect x="340" y="15" width="320" height="{HEIGHT - 30}" rx="5" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
    <text x="355" y="42" fill="{TEXT_PRIMARY}" font-size="12" font-weight="700">MOST USED LANGUAGES</text>
    <line x1="355" y1="52" x2="645" y2="52" stroke="{BORDER_MUTED}" stroke-width="1"/>
    
    <rect x="355" y="66" width="290" height="7" rx="3.5" fill="{BORDER_MUTED}"/>
''')

bar_x = 355
bar_w_total = 290
for name, pct, col in LANGS:
    seg_w = round((pct / 100.0) * bar_w_total, 1)
    svg_lines.append(f'    <rect x="{bar_x}" y="66" width="{seg_w}" height="7" rx="2" fill="{col}"/>\n')
    bar_x += seg_w

svg_lines.append('\n')
start_y = 94
for i, (name, pct, col) in enumerate(LANGS):
    c_x = 355 if i < 3 else 505
    c_y = start_y + (i % 3) * 23
    svg_lines.append(f'''    <circle cx="{c_x + 5}" cy="{c_y - 4}" r="3" fill="{col}"/>
    <text x="{c_x + 14}" y="{c_y}" fill="{TEXT_MUTED}" font-size="9.5">{name}</text>
    <text x="{c_x + 120}" y="{c_y}" fill="{TEXT_PRIMARY}" font-size="9.5" font-weight="600" text-anchor="end">{pct:.1f}%</text>
''')

svg_lines.append(f'''  </g>

  <!-- Card 3: Streak -->
  <g class="code-mono">
    <rect x="675" y="15" width="310" height="{HEIGHT - 30}" rx="5" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
    <text x="690" y="42" fill="{TEXT_PRIMARY}" font-size="12" font-weight="700">CONTRIBUTION STREAK</text>
    <line x1="690" y1="52" x2="970" y2="52" stroke="{BORDER_MUTED}" stroke-width="1"/>
    
    <text x="695" y="80" fill="{TEXT_MUTED}" font-size="10.5">Current Streak:</text>
    <text x="965" y="80" fill="{TEXT_PRIMARY}" font-size="12" font-weight="700" text-anchor="end">2 Days</text>
    
    <text x="695" y="108" fill="{TEXT_MUTED}" font-size="10.5">Longest Streak:</text>
    <text x="965" y="108" fill="{TEXT_PRIMARY}" font-size="12" font-weight="700" text-anchor="end">5 Days</text>
    
    <text x="695" y="136" fill="{TEXT_MUTED}" font-size="10.5">Total Activity:</text>
    <text x="965" y="136" fill="{TEXT_PRIMARY}" font-size="12" font-weight="700" text-anchor="end">580 Events</text>
  </g>
</svg>
''')

target_path = '/Users/guptanaman/.gemini/antigravity-ide/scratch/namaninnovates/assets/github_metrics.svg'
with open(target_path, 'w') as f:
    f.writelines(svg_lines)

print("Clean Metrics SVG generated!")
