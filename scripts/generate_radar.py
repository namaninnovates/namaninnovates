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

WIDTH, HEIGHT = 1000, 520
CX, CY = 500, 270
R_MIN = 60
R_MAX = 195

BG_COLOR = (13, 17, 23, 255)       # #0d1117
PANEL_BG = (22, 27, 34, 255)       # #161b22
BORDER_DEFAULT = (48, 54, 61, 255) # #30363d
BORDER_MUTED = (33, 38, 45, 255)   # #21262d
TEXT_PRIMARY = (240, 246, 252, 255)# #f0f6fc
TEXT_MUTED = (139, 148, 158, 255)  # #8b949e

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
    angle_rad = frac_w * 2 * math.pi - math.pi / 2
    angle_deg = math.degrees(angle_rad) % 360
    
    for day in week["contributionDays"]:
        count = day["contributionCount"]
        d_idx = (day["weekday"] + 6) % 7
        r = R_MIN + (d_idx / 6.0) * (R_MAX - R_MIN)
        
        px = CX + r * math.cos(angle_rad)
        py = CY + r * math.sin(angle_rad)
        day_nodes.append({
            "x": px, "y": py, "r": r,
            "angle_deg": angle_deg,
            "angle_rad": angle_rad,
            "count": count
        })

frames_dir = os.path.join(os.path.dirname(__file__), "../assets/radar_temp_frames")
if os.path.exists(frames_dir):
    shutil.rmtree(frames_dir)
os.makedirs(frames_dir, exist_ok=True)

TOTAL_FRAMES = 72
SWEEP_TRAIL_DEG = 55.0

months = ["AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL"]

for frame_idx in range(TOTAL_FRAMES):
    sweep_angle_deg = (frame_idx / float(TOTAL_FRAMES)) * 360.0
    sweep_angle_rad = math.radians(sweep_angle_deg - 90.0)
    
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], radius=6, outline=BORDER_DEFAULT, width=1)
    
    draw.rounded_rectangle([(15, 12), (WIDTH - 15, 44)], radius=4, fill=PANEL_BG, outline=BORDER_DEFAULT, width=1)
    draw.text((28, 22), "RADIAL RADAR TELEMETRY // 360° RESCANNING SWEEP", font=font_mono_sm, fill=TEXT_PRIMARY)
    draw.text((WIDTH - 320, 22), f"TOTAL: {total_commits} COMMITS | ACTIVE SCAN", font=font_mono_xs, fill=TEXT_MUTED)
    
    for d in range(7):
        r = R_MIN + (d / 6.0) * (R_MAX - R_MIN)
        draw.ellipse([(CX - r, CY - r), (CX + r, CY + r)], outline=BORDER_MUTED, width=1)
        
    draw.ellipse([(CX - (R_MAX + 15), CY - (R_MAX + 15)), (CX + (R_MAX + 15), CY + (R_MAX + 15))], outline=BORDER_DEFAULT, width=1)
    draw.ellipse([(CX - (R_MIN - 12), CY - (R_MIN - 12)), (CX + (R_MIN - 12), CY + (R_MIN - 12))], outline=BORDER_DEFAULT, width=1)
    
    for m_idx in range(12):
        a_deg = m_idx * 30.0 - 90.0
        a_rad = math.radians(a_deg)
        x1 = CX + (R_MIN - 12) * math.cos(a_rad)
        y1 = CY + (R_MIN - 12) * math.sin(a_rad)
        x2 = CX + (R_MAX + 15) * math.cos(a_rad)
        y2 = CY + (R_MAX + 15) * math.sin(a_rad)
        draw.line([(x1, y1), (x2, y2)], fill=BORDER_MUTED, width=1)
        
        lx = CX + (R_MAX + 28) * math.cos(a_rad)
        ly = CY + (R_MAX + 28) * math.sin(a_rad) - 5
        draw.text((lx - 8, ly), months[m_idx], font=font_mono_xs, fill=TEXT_MUTED)
        
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    
    steps = 25
    for s in range(steps):
        frac = s / float(steps)
        t_deg = (sweep_angle_deg - (1.0 - frac) * SWEEP_TRAIL_DEG) % 360.0
        t_rad = math.radians(t_deg - 90.0)
        t_deg_next = (sweep_angle_deg - (1.0 - (s + 1) / float(steps)) * SWEEP_TRAIL_DEG) % 360.0
        t_rad_next = math.radians(t_deg_next - 90.0)
        alpha = int(45 * (frac ** 2.2))
        
        p1 = (CX + (R_MIN - 10) * math.cos(t_rad), CY + (R_MIN - 10) * math.sin(t_rad))
        p2 = (CX + (R_MAX + 15) * math.cos(t_rad), CY + (R_MAX + 15) * math.sin(t_rad))
        p3 = (CX + (R_MAX + 15) * math.cos(t_rad_next), CY + (R_MAX + 15) * math.sin(t_rad_next))
        p4 = (CX + (R_MIN - 10) * math.cos(t_rad_next), CY + (R_MIN - 10) * math.sin(t_rad_next))
        ov_draw.polygon([p1, p2, p3, p4], fill=(240, 246, 252, alpha))
        
    beam_x = CX + (R_MAX + 15) * math.cos(sweep_angle_rad)
    beam_y = CY + (R_MAX + 15) * math.sin(sweep_angle_rad)
    ov_draw.line([(CX, CY), (beam_x, beam_y)], fill=(255, 255, 255, 220), width=2)
    
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    for node in day_nodes:
        ang = node["angle_deg"]
        diff = (sweep_angle_deg - ang) % 360.0
        if diff < SWEEP_TRAIL_DEG:
            afterglow = 1.0 - (diff / SWEEP_TRAIL_DEG) ** 1.5
        else:
            afterglow = 0.0
            
        count = node["count"]
        nx, ny = node["x"], node["y"]
        
        if count == 0:
            if afterglow > 0.3:
                v = int(33 + 60 * afterglow)
                draw.ellipse([(nx - 1.2, ny - 1.2), (nx + 1.2, ny + 1.2)], fill=(v, v, v, 255))
            else:
                draw.ellipse([(nx - 1.0, ny - 1.0), (nx + 1.0, ny + 1.0)], fill=BORDER_MUTED)
        else:
            if count < 5:
                base_col = (110, 118, 129, 255)
                r_base = 1.8
            elif count < 15:
                base_col = (139, 148, 158, 255)
                r_base = 2.4
            elif count < 30:
                base_col = (201, 209, 217, 255)
                r_base = 3.2
            else:
                base_col = (240, 246, 252, 255)
                r_base = 4.2
                
            if afterglow > 0.05:
                glow_r = r_base + 1.5 * afterglow
                r_c = int(base_col[0] + (255 - base_col[0]) * afterglow)
                g_c = int(base_col[1] + (255 - base_col[1]) * afterglow)
                b_c = int(base_col[2] + (255 - base_col[2]) * afterglow)
                draw.ellipse([(nx - glow_r, ny - glow_r), (nx + glow_r, ny + glow_r)], fill=(r_c, g_c, b_c, 255))
                
                if count >= 30:
                    sp_r = R_MAX + 10 + min(count, 50) * 0.4
                    sp_x = CX + sp_r * math.cos(node["angle_rad"])
                    sp_y = CY + sp_r * math.sin(node["angle_rad"])
                    flare_a = int(255 * afterglow)
                    draw.line([(nx, ny), (sp_x, sp_y)], fill=(240, 246, 252, flare_a), width=1)
                    draw.ellipse([(sp_x - 1.5, sp_y - 1.5), (sp_x + 1.5, sp_y + 1.5)], fill=(255, 255, 255, flare_a))
            else:
                draw.ellipse([(nx - r_base, ny - r_base), (nx + r_base, ny + r_base)], fill=base_col)
                if count >= 30:
                    sp_r = R_MAX + 8 + min(count, 50) * 0.4
                    sp_x = CX + sp_r * math.cos(node["angle_rad"])
                    sp_y = CY + sp_r * math.sin(node["angle_rad"])
                    draw.line([(nx, ny), (sp_x, sp_y)], fill=BORDER_DEFAULT, width=1)

    hub_phase = (frame_idx / float(TOTAL_FRAMES) * 2.0) % 1.0
    hub_r = 4 + hub_phase * 18
    hub_alpha = int(180 * (1.0 - hub_phase))
    draw.ellipse([(CX - hub_r, CY - hub_r), (CX + hub_r, CY + hub_r)], outline=(240, 246, 252, hub_alpha), width=1)
    
    draw.ellipse([(CX - 3, CY - 3), (CX + 3, CY + 3)], fill=TEXT_PRIMARY)
    draw.line([(CX - 8, CY), (CX + 8, CY)], fill=TEXT_PRIMARY, width=1)
    draw.line([(CX, CY - 8), (CX, CY + 8)], fill=TEXT_PRIMARY, width=1)

    draw.rounded_rectangle([(35, 180), (170, 250)], radius=4, fill=PANEL_BG, outline=BORDER_DEFAULT, width=1)
    draw.text((45, 192), "// SCAN BEARING", font=font_mono_xs, fill=TEXT_MUTED)
    draw.text((45, 210), f"{int(sweep_angle_deg):03d}° SWEEP", font=font_mono_lg, fill=TEXT_PRIMARY)
    draw.text((45, 230), "STATUS: RESCANNING", font=font_mono_xs, fill=TEXT_MUTED)

    draw.rounded_rectangle([(WIDTH - 170, 180), (WIDTH - 35, 250)], radius=4, fill=PANEL_BG, outline=BORDER_DEFAULT, width=1)
    draw.text((WIDTH - 160, 192), "// TOTAL COMMITS", font=font_mono_xs, fill=TEXT_MUTED)
    draw.text((WIDTH - 160, 210), f"{total_commits} EVENTS", font=font_mono_lg, fill=TEXT_PRIMARY)
    draw.text((WIDTH - 160, 230), "MAX PEAK: 65/DAY", font=font_mono_xs, fill=TEXT_MUTED)

    draw.rounded_rectangle([(15, HEIGHT - 34), (WIDTH - 15, HEIGHT - 12)], radius=3, fill=PANEL_BG, outline=BORDER_DEFAULT, width=1)
    draw.text((26, HEIGHT - 23), "// 360° CONTINUOUS RESCANNING RADAR | RANGE: 52 WEEKS | GITHUB.COM/NAMANINNOVATES", font=font_mono_xs, fill=TEXT_MUTED)

    img.save(f"{frames_dir}/frame_{frame_idx:03d}.png")

target_gif = os.path.join(os.path.dirname(__file__), "../assets/radial_radar.gif")

ffmpeg_bin = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"
subprocess.run([
    ffmpeg_bin, "-y", "-r", "24",
    "-i", f"{frames_dir}/frame_%03d.png",
    "-vf", "fps=24,scale=1000:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=32:reserve_transparent=0[p];[s1][p]paletteuse=dither=none:diff_mode=rectangle",
    target_gif
], check=True)

shutil.rmtree(frames_dir)
print("Rescanning Radar GIF compiled successfully at:", target_gif)
