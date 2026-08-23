import os

WIDTH, HEIGHT = 1000, 195
PANEL_BG = "#161b22"
BORDER_DEFAULT = "#30363d"
TEXT_PRIMARY = "#f0f6fc"
TEXT_MUTED = "#8b949e"

TECH = [
    "JAVA", "C / C++", "PYTHON", "TYPESCRIPT", "JAVASCRIPT", "REACT",
    "NEXT.JS", "NODE.JS", "POSTGRESQL", "NEON", "SUPABASE", "DOCKER",
    "GCP", "VERCEL", "ANTIGRAVITY", "GOOGLE VEO", "STITCH", "TAILWIND",
    "LINUX", "GIT", "FIGMA", "PREMIERE PRO"
]

cols = 6
chip_w = 153
chip_h = 32
start_x = 22
start_y = 38
gap_x = 8
gap_y = 6

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

  <!-- Header -->
  <text x="24" y="24" fill="{TEXT_PRIMARY}" font-size="11" font-weight="700" class="code-mono" letter-spacing="0.5">TECH STACK</text>
  <text x="{WIDTH - 120}" y="24" fill="{TEXT_MUTED}" font-size="9" font-weight="500" class="code-mono">{len(TECH)} TECHNOLOGIES</text>

  <g class="code-mono">
''')

for i, name in enumerate(TECH):
    r_idx = i // cols
    c_idx = i % cols
    x = start_x + c_idx * (chip_w + gap_x)
    y = start_y + r_idx * (chip_h + gap_y)
    
    svg_lines.append(f'''    <g>
      <rect x="{x}" y="{y}" width="{chip_w}" height="{chip_h}" rx="4" fill="{PANEL_BG}" stroke="{BORDER_DEFAULT}" stroke-width="1"/>
      <circle cx="{x + 12}" cy="{y + 16}" r="2" fill="{TEXT_PRIMARY}"/>
      <text x="{x + 20}" y="{y + 20}" fill="{TEXT_PRIMARY}" font-size="10" font-weight="600">{name}</text>
    </g>
''')

svg_lines.append('''  </g>
</svg>
''')

target_path = os.path.join(os.path.dirname(__file__), '../assets/tech_stack.svg')
os.makedirs(os.path.dirname(target_path), exist_ok=True)
with open(target_path, 'w') as f:
    f.writelines(svg_lines)

print(f"Tech Stack SVG updated with {len(TECH)} technologies!")
