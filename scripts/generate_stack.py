import os

WIDTH, HEIGHT = 1000, 140
PANEL_BG = "#161b22"
BORDER_DEFAULT = "#30363d"
BORDER_MUTED = "#21262d"
TEXT_PRIMARY = "#f0f6fc"
TEXT_MUTED = "#8b949e"

TECH = [
    ("JAVA", "Backend / Core"),
    ("C / C++", "Low-Level / Perf"),
    ("PYTHON", "Data / AI / Scripting"),
    ("TYPESCRIPT", "Strict Full-Stack"),
    ("JAVASCRIPT", "Web Engine"),
    ("REACT", "UI Components"),
    ("NEXT.JS", "SSR / Edge Framework"),
    ("NODE.JS", "Async Runtime"),
    ("EXPRESS", "REST Microservices"),
    ("TAILWIND", "Design Systems"),
    ("DOCKER", "Containerization"),
    ("LINUX", "Kernel / POSIX"),
    ("GIT", "VCS / CI-CD"),
    ("FIGMA", "Interface Design"),
]

svg_lines = []
svg_lines.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%">
  <defs>
    <style>
      .code-mono {{
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      }}
      @keyframes badgePulse {{
        0%, 100% {{ border-color: {BORDER_DEFAULT}; }}
        50% {{ border-color: {TEXT_PRIMARY}; }}
      }}
      @keyframes sweepScan {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
      }}
      .chip {{
        transition: all 0.3s ease;
      }}
    </style>
  </defs>

  <!-- 100% Transparent Outer Frame -->
  <rect width="{WIDTH}" height="{HEIGHT}" rx="6" fill="none" stroke="{BORDER_DEFAULT}" stroke-width="1"/>

  <!-- Header Strip -->
  <rect x="15" y="10" width="{WIDTH - 30}" height="26" rx="4" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
  <text x="26" y="27" fill="{TEXT_PRIMARY}" font-size="11" font-weight="600" class="code-mono">// STACK MATRIX // MONOCHROME CORE</text>
  <text x="{WIDTH - 165}" y="27" fill="{TEXT_MUTED}" font-size="9" font-weight="500" class="code-mono">14 ACTIVE MODULES</text>

  <!-- Badges Grid (2 rows of 7 chips) -->
  <g class="code-mono">
''')

cols = 7
chip_w = 132
chip_h = 40
start_x = 22
start_y = 46
gap_x = 7
gap_y = 6

for i, (name, role) in enumerate(TECH):
    r_idx = i // cols
    c_idx = i % cols
    x = start_x + c_idx * (chip_w + gap_x)
    y = start_y + r_idx * (chip_h + gap_y)
    
    svg_lines.append(f'''    <!-- {name} -->
    <g class="chip">
      <rect x="{x}" y="{y}" width="{chip_w}" height="{chip_h}" rx="5" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
      <circle cx="{x + 12}" cy="{y + 14}" r="2" fill="{TEXT_PRIMARY}"/>
      <text x="{x + 20}" y="{y + 17}" fill="{TEXT_PRIMARY}" font-size="10.5" font-weight="700">{name}</text>
      <text x="{x + 12}" y="{y + 31}" fill="{TEXT_MUTED}" font-size="7.5" font-weight="500">{role}</text>
    </g>
''')

svg_lines.append('''  </g>
</svg>
''')

target_path = '/Users/guptanaman/.gemini/antigravity-ide/scratch/namaninnovates/assets/tech_stack.svg'
with open(target_path, 'w') as f:
    f.writelines(svg_lines)

print("Monochrome Tech Stack SVG generated at:", target_path)
