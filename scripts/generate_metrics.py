import json, os

WIDTH, HEIGHT = 1000, 220
PANEL_BG = "#161b22"
BORDER_DEFAULT = "#30363d"
BORDER_MUTED = "#21262d"
TEXT_PRIMARY = "#f0f6fc"
TEXT_MUTED = "#8b949e"

# Monochrome language palette (Grayscale tonal hierarchy - 0 colors)
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
      @keyframes pulseFlame {{
        0%, 100% {{ transform: scale(1); opacity: 0.9; }}
        50% {{ transform: scale(1.08); opacity: 1; }}
      }}
      @keyframes progressGrow {{
        0% {{ width: 0; }}
        100% {{ width: 100%; }}
      }}
      .flame-icon {{
        transform-origin: 840px 105px;
        animation: pulseFlame 2.5s ease-in-out infinite;
      }}
    </style>
  </defs>

  <!-- 100% Transparent Outer Frame -->
  <rect width="{WIDTH}" height="{HEIGHT}" rx="6" fill="none" stroke="{BORDER_DEFAULT}" stroke-width="1"/>

  <!-- Card 1: Core Telemetry Stats -->
  <g class="code-mono">
    <rect x="15" y="15" width="310" height="{HEIGHT - 30}" rx="6" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
    
    <text x="30" y="42" fill="{TEXT_PRIMARY}" font-size="12" font-weight="700" letter-spacing="0.5">// TELEMETRY STATS</text>
    <line x1="30" y1="52" x2="310" y2="52" stroke="{BORDER_MUTED}" stroke-width="1"/>
    
    <text x="30" y="78" fill="{TEXT_MUTED}" font-size="10">TOTAL COMMITS (YTD):</text>
    <text x="280" y="78" fill="{TEXT_PRIMARY}" font-size="11" font-weight="700" text-anchor="end">580</text>
    
    <text x="30" y="106" fill="{TEXT_MUTED}" font-size="10">STARS EARNED:</text>
    <text x="280" y="106" fill="{TEXT_PRIMARY}" font-size="11" font-weight="700" text-anchor="end">1</text>
    
    <text x="30" y="134" fill="{TEXT_MUTED}" font-size="10">ACTIVE REPOSITORIES:</text>
    <text x="280" y="134" fill="{TEXT_PRIMARY}" font-size="11" font-weight="700" text-anchor="end">12</text>
    
    <text x="30" y="162" fill="{TEXT_MUTED}" font-size="10">GLOBAL CLIENT HUBS:</text>
    <text x="280" y="162" fill="{TEXT_PRIMARY}" font-size="11" font-weight="700" text-anchor="end">12</text>
    
    <text x="30" y="190" fill="{TEXT_MUTED}" font-size="8.5">// AUTH: NAMANINNOVATES</text>
  </g>

  <!-- Card 2: Monochrome Language Distribution -->
  <g class="code-mono">
    <rect x="340" y="15" width="320" height="{HEIGHT - 30}" rx="6" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
    
    <text x="355" y="42" fill="{TEXT_PRIMARY}" font-size="12" font-weight="700" letter-spacing="0.5">// LANGUAGE MATRIX</text>
    <line x1="355" y1="52" x2="645" y2="52" stroke="{BORDER_MUTED}" stroke-width="1"/>
    
    <!-- Multi-Segment Monochrome Progress Bar -->
    <rect x="355" y="66" width="290" height="8" rx="4" fill="{BORDER_MUTED}"/>
''')

# Build progressive bar
bar_x = 355
bar_w_total = 290
for name, pct, col in LANGS:
    seg_w = round((pct / 100.0) * bar_w_total, 1)
    svg_lines.append(f'    <rect x="{bar_x}" y="66" width="{seg_w}" height="8" rx="2" fill="{col}"/>\n')
    bar_x += seg_w

svg_lines.append('\n    <!-- Language Legend -->\n')
start_y = 96
for i, (name, pct, col) in enumerate(LANGS):
    c_x = 355 if i < 3 else 505
    c_y = start_y + (i % 3) * 26
    svg_lines.append(f'''    <circle cx="{c_x + 5}" cy="{c_y - 4}" r="3.5" fill="{col}"/>
    <text x="{c_x + 15}" y="{c_y}" fill="{TEXT_MUTED}" font-size="9.5">{name}:</text>
    <text x="{c_x + 120}" y="{c_y}" fill="{TEXT_PRIMARY}" font-size="9.5" font-weight="600" text-anchor="end">{pct:.1f}%</text>
''')

svg_lines.append(f'''  </g>

  <!-- Card 3: Streak Telemetry -->
  <g class="code-mono">
    <rect x="675" y="15" width="310" height="{HEIGHT - 30}" rx="6" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
    
    <text x="690" y="42" fill="{TEXT_PRIMARY}" font-size="12" font-weight="700" letter-spacing="0.5">// STREAK VELOCITY</text>
    <line x1="690" y1="52" x2="970" y2="52" stroke="{BORDER_MUTED}" stroke-width="1"/>
    
    <!-- Circular Flame Dial -->
    <g class="flame-icon">
      <circle cx="830" cy="115" r="38" fill="none" stroke="{BORDER_DEFAULT}" stroke-width="2"/>
      <circle cx="830" cy="115" r="34" fill="none" stroke="{TEXT_PRIMARY}" stroke-width="1.5" stroke-dasharray="4 4"/>
      <text x="830" y="112" fill="{TEXT_PRIMARY}" font-size="18" font-weight="800" text-anchor="middle">5</text>
      <text x="830" y="128" fill="{TEXT_MUTED}" font-size="7.5" font-weight="600" text-anchor="middle">DAYS MAX</text>
    </g>
    
    <text x="695" y="90" fill="{TEXT_MUTED}" font-size="8.5">TOTAL EVENTS</text>
    <text x="695" y="110" fill="{TEXT_PRIMARY}" font-size="14" font-weight="700">580</text>
    
    <text x="695" y="145" fill="{TEXT_MUTED}" font-size="8.5">CURRENT STREAK</text>
    <text x="695" y="165" fill="{TEXT_PRIMARY}" font-size="14" font-weight="700">2 DAYS</text>
    
    <text x="690" y="190" fill="{TEXT_MUTED}" font-size="8.5">// CONTINUOUS ACTIVE DEPLOYMENT</text>
  </g>
</svg>
''')

target_path = '/Users/guptanaman/.gemini/antigravity-ide/scratch/namaninnovates/assets/github_metrics.svg'
with open(target_path, 'w') as f:
    f.writelines(svg_lines)

print("Monochrome GitHub Metrics SVG generated at:", target_path)
