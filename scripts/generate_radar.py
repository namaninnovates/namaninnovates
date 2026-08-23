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

# 1080P HD RETINA RESOLUTION (2000x1040)
WIDTH, HEIGHT = 2000, 1040
CX, CY = 1000, 540
R_MIN = 120
R_MAX = 390

BG_COLOR = (13, 17, 23, 255)       # #0d1117
PANEL_BG = (22, 27, 34, 255)       # #161b22
BORDER_DEFAULT = (48, 54, 61, 255) # #30363d
BORDER_MUTED = (33, 38, 45, 255)   # #21262d
TEXT_PRIMARY = (240, 246, 252, 255)# #f0f6fc
TEXT_MUTED = (139, 148, 158, 255)  # #8b949e

try:
    font_mono_xs = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)
    font_mono_sm = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22)
    font_mono_lg = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 26)
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

TOTAL_FRAMES = 96
SWEEP_TRAIL_DEG = 135.0

months = ["AUG", "SEP", "OCT", "NOV", "DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL"]

for frame_idx in range(TOTAL_FRAMES):
    sweep_angle_deg = (frame_idx / float(TOTAL_FRAMES)) * 360.0
    sweep_angle_rad = math.radians(sweep_angle_deg - 90.0)
    
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Outer Border
    draw.rounded_rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], radius=12, outline=BORDER_DEFAULT, width=2)
    
    # Header Bar
    draw.rounded_rectangle([(30, 24), (WIDTH - 30, 88)], radius=8, fill=PANEL_BG, outline=BORDER_DEFAULT, width=2)
    draw.text((56, 44), "RADIAL RADAR TELEMETRY // 360° PPI SCANNER", font=font_mono_sm, fill=TEXT_PRIMARY)
    draw.text((WIDTH - 650, 44), f"TOTAL: {total_commits} COMMITS | 52 WEEKS ACTIVE", font=font_mono_xs, fill=TEXT_MUTED)
    
    # Concentric Orbit Rings (7 Weekday Circles)
    for d in range(7):
        r = R_MIN + (d / 6.0) * (R_MAX - R_MIN)
        draw.ellipse([(CX - r, CY - r), (CX + r, CY + r)], outline=BORDER_MUTED, width=2)
        
    draw.ellipse([(CX - (R_MAX + 30), CY - (R_MAX + 30)), (CX + (R_MAX + 30), CY + (R_MAX + 30))], outline=BORDER_DEFAULT, width=2)
    draw.ellipse([(CX - (R_MIN - 24), CY - (R_MIN - 24)), (CX + (R_MIN - 24), CY + (R_MIN - 24))], outline=BORDER_DEFAULT, width=2)
    
    # Spokes & Month Labels
    for m_idx in range(12):
        a_deg = m_idx * 30.0
        a_rad = math.radians(a_deg - 90.0)
        x1 = CX + (R_MIN - 24) * math.cos(a_rad)
        y1 = CY + (R_MIN - 24) * math.sin(a_rad)
        x2 = CX + (R_MAX + 30) * math.cos(a_rad)
        y2 = CY + (R_MAX + 30) * math.sin(a_rad)
        draw.line([(x1, y1), (x2, y2)], fill=BORDER_MUTED, width=2)
        
        lx = CX + (R_MAX + 56) * math.cos(a_rad)
        ly = CY + (R_MAX + 56) * math.sin(a_rad) - 10
        draw.text((lx - 16, ly), months[m_idx], font=font_mono_xs, fill=TEXT_MUTED)

    # 1. Base Dormant Nodes
    for node in day_nodes:
        ang = node["angle_deg"]
        diff = (sweep_angle_deg - ang) % 360.0
        if diff >= SWEEP_TRAIL_DEG:
            count = node["count"]
            nx, ny = node["x"], node["y"]
            if count == 0:
                draw.ellipse([(nx - 2.0, ny - 2.0), (nx + 2.0, ny + 2.0)], fill=(33, 38, 45, 255))
            elif count < 5:
                draw.ellipse([(nx - 3.2, ny - 3.2), (nx + 3.2, ny + 3.2)], fill=(65, 75, 88, 255))
            elif count < 15:
                draw.ellipse([(nx - 4.4, ny - 4.4), (nx + 4.4, ny + 4.4)], fill=(95, 106, 120, 255))
            elif count < 30:
                draw.ellipse([(nx - 5.6, ny - 5.6), (nx + 5.6, ny + 5.6)], fill=(125, 138, 155, 255))
            else:
                draw.ellipse([(nx - 6.8, ny - 6.8), (nx + 6.8, ny + 6.8)], fill=(160, 175, 195, 255))

    # 2. Phosphor Sweep Sector Gradient
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    
    steps = 60
    for s in range(steps):
        frac = s / float(steps)
        t_deg = (sweep_angle_deg - (1.0 - frac) * SWEEP_TRAIL_DEG) % 360.0
        t_rad = math.radians(t_deg - 90.0)
        t_deg_next = (sweep_angle_deg - (1.0 - (s + 1) / float(steps)) * SWEEP_TRAIL_DEG) % 360.0
        t_rad_next = math.radians(t_deg_next - 90.0)
        
        alpha = int(55 * (frac ** 2.0))
        p1 = (CX + (R_MIN - 20) * math.cos(t_rad), CY + (R_MIN - 20) * math.sin(t_rad))
        p2 = (CX + (R_MAX + 30) * math.cos(t_rad), CY + (R_MAX + 30) * math.sin(t_rad))
        p3 = (CX + (R_MAX + 30) * math.cos(t_rad_next), CY + (R_MAX + 30) * math.sin(t_rad_next))
        p4 = (CX + (R_MIN - 20) * math.cos(t_rad_next), CY + (R_MIN - 20) * math.sin(t_rad_next))
        ov_draw.polygon([p1, p2, p3, p4], fill=(240, 246, 252, alpha))
        
    # Main Sweep Beam Line (4px width + glow)
    beam_x = CX + (R_MAX + 30) * math.cos(sweep_angle_rad)
    beam_y = CY + (R_MAX + 30) * math.sin(sweep_angle_rad)
    ov_draw.line([(CX, CY), (beam_x, beam_y)], fill=(255, 255, 255, 245), width=4)
    ov_draw.line([(CX, CY), (beam_x, beam_y)], fill=(240, 246, 252, 60), width=8)
    
    # 3. High-Contrast Phosphor Excitation on Sweep Contact
    for node in day_nodes:
        ang = node["angle_deg"]
        diff = (sweep_angle_deg - ang) % 360.0
        if diff < SWEEP_TRAIL_DEG:
            decay = ((SWEEP_TRAIL_DEG - diff) / SWEEP_TRAIL_DEG) ** 1.3
            count = node["count"]
            nx, ny = node["x"], node["y"]
            
            if count == 0:
                v = int(33 + (85 - 33) * decay)
                ov_draw.ellipse([(nx - 2.2, ny - 2.2), (nx + 2.2, ny + 2.2)], fill=(v, v, v, 255))
            else:
                if count < 5:
                    base_r, base_g, base_b = 85, 96, 110
                    base_radius = 3.6
                elif count < 15:
                    base_r, base_g, base_b = 130, 142, 160
                    base_radius = 4.8
                elif count < 30:
                    base_r, base_g, base_b = 180, 195, 215
                    base_radius = 6.4
                else:
                    base_r, base_g, base_b = 220, 235, 255
                    base_radius = 8.4
                
                curr_r = int(base_r + (255 - base_r) * (decay ** 0.8))
                curr_g = int(base_g + (255 - base_g) * (decay ** 0.8))
                curr_b = int(base_b + (255 - base_b) * (decay ** 0.8))
                
                glow_radius = base_radius + 3.2 * decay
                ov_draw.ellipse([(nx - glow_radius, ny - glow_radius), (nx + glow_radius, ny + glow_radius)], fill=(curr_r, curr_g, curr_b, 255))
                
                if count >= 20 and decay > 0.2:
                    flare_len = 16 + (min(count, 65) / 65.0) * 44.0 * decay
                    sp_x = CX + (node["r"] + flare_len) * math.cos(node["angle_rad"])
                    sp_y = CY + (node["r"] + flare_len) * math.sin(node["angle_rad"])
                    flare_alpha = int(250 * decay)
                    ov_draw.line([(nx, ny), (sp_x, sp_y)], fill=(240, 246, 252, flare_alpha), width=2)
                    ov_draw.ellipse([(sp_x - 2.6, sp_y - 2.6), (sp_x + 2.6, sp_y + 2.6)], fill=(255, 255, 255, flare_alpha))

    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Center Hub Pulse
    hub_phase = (frame_idx / float(TOTAL_FRAMES) * 2.0) % 1.0
    hub_r = 8 + hub_phase * 40
    hub_alpha = int(190 * (1.0 - hub_phase))
    draw.ellipse([(CX - hub_r, CY - hub_r), (CX + hub_r, CY + hub_r)], outline=(240, 246, 252, hub_alpha), width=2)
    draw.ellipse([(CX - 6, CY - 6), (CX + 6, CY + 6)], fill=TEXT_PRIMARY)
    draw.line([(CX - 16, CY), (CX + 16, CY)], fill=TEXT_PRIMARY, width=2)
    draw.line([(CX, CY - 16), (CX, CY + 16)], fill=TEXT_PRIMARY, width=2)

    # Left & Right HUD Panels
    draw.rounded_rectangle([(70, 360), (340, 500)], radius=8, fill=PANEL_BG, outline=BORDER_DEFAULT, width=2)
    draw.text((90, 384), "// SCAN BEARING", font=font_mono_xs, fill=TEXT_MUTED)
    draw.text((90, 420), f"{int(sweep_angle_deg):03d}° PPI", font=font_mono_lg, fill=TEXT_PRIMARY)
    draw.text((90, 460), "STATUS: RESCANNING", font=font_mono_xs, fill=TEXT_MUTED)

    draw.rounded_rectangle([(WIDTH - 340, 360), (WIDTH - 70, 500)], radius=8, fill=PANEL_BG, outline=BORDER_DEFAULT, width=2)
    draw.text((WIDTH - 320, 384), "// TOTAL COMMITS", font=font_mono_xs, fill=TEXT_MUTED)
    draw.text((WIDTH - 320, 420), f"{total_commits} EVENTS", font=font_mono_lg, fill=TEXT_PRIMARY)
    draw.text((WIDTH - 320, 460), "MAX PEAK: 65/DAY", font=font_mono_xs, fill=TEXT_MUTED)

    # Footer Bar
    draw.rounded_rectangle([(30, HEIGHT - 68), (WIDTH - 30, HEIGHT - 24)], radius=6, fill=PANEL_BG, outline=BORDER_DEFAULT, width=2)
    draw.text((52, HEIGHT - 46), "// 360° CONTINUOUS RESCANNING RADAR | RANGE: 52 WEEKS | GITHUB.COM/NAMANINNOVATES", font=font_mono_xs, fill=TEXT_MUTED)

    img.save(f"{frames_dir}/frame_{frame_idx:03d}.png")

target_gif = os.path.join(os.path.dirname(__file__), "../assets/radial_radar.gif")
ffmpeg_bin = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"

subprocess.run([
    ffmpeg_bin, "-y", "-r", "20",
    "-i", f"{frames_dir}/frame_%03d.png",
    "-vf", "fps=20,scale=2000:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle",
    target_gif
], check=True)

shutil.rmtree(frames_dir)
print("1080p HD Radar GIF successfully generated at:", target_gif)
