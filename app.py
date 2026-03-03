import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import pillow_avif
import os
import io
import math

st.set_page_config(layout="centered", page_title="Formula Rossa Post Generator")

st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: white; }
    .stSelectbox label, .stTextInput label, .stNumberInput label { color: #ff1801 !important; font-weight: bold; }
    .stButton button { background-color: #ff1801; color: white; border: none; font-weight: bold; width: 100%; }
    .stButton button:hover { background-color: #cc1200; }
    h1 { color: #ff1801 !important; }
    .stTabs [data-baseweb="tab"] { color: #aaa; }
    .stTabs [aria-selected="true"] { color: #ff1801 !important; border-bottom: 2px solid #ff1801; }
    .stDownloadButton button { background-color: #222; border: 1px solid #ff1801; color: #ff1801; }
</style>
""", unsafe_allow_html=True)

st.title("🏎️ Formula Rossa — Post Generator")

DRIVER_FOLDER = "Drivers"

# ─── FONT LOADER ──────────────────────────────────────────────────────────────
def get_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "Arial Bold.ttf" if bold else "Arial.ttf",
    ]
    for f in candidates:
        try:
            return ImageFont.truetype(f, size)
        except:
            pass
    return ImageFont.load_default()

# ─── DRIVER HELPERS ───────────────────────────────────────────────────────────
def load_driver_image(filename):
    path = os.path.join(DRIVER_FOLDER, filename)
    return Image.open(path).convert("RGBA")

def clean_driver_name(filename):
    name = filename
    for ext in [".avif", ".png", ".jpg", ".jpeg", ".webp"]:
        name = name.replace(ext, "")
    for token in ["2026", "2025", "2024", "01right", "01left", "right", "left", "_", "-"]:
        name = name.replace(token, " ")
    return " ".join(name.split()).upper()

def get_drivers():
    if not os.path.exists(DRIVER_FOLDER):
        return []
    exts = (".avif", ".png", ".jpg", ".jpeg", ".webp")
    return [f for f in os.listdir(DRIVER_FOLDER) if f.lower().endswith(exts)]

# ─── DRAWING HELPERS ──────────────────────────────────────────────────────────
W, H = 1080, 1350

def draw_centered_text(draw, text, y, font, color=(255, 255, 255), shadow=True):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) / 2
    if shadow:
        for dx, dy in [(-4, 4), (4, 4), (-4, -4), (4, -4)]:
            draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=font, fill=color)

def draw_name_badge(draw, name, y, font):
    bbox = draw.textbbox((0, 0), name, font=font)
    tw = bbox[2] - bbox[0]
    pad_x, pad_y = 30, 12
    rx = (W - tw) / 2 - pad_x
    ry = y - pad_y
    rw = tw + pad_x * 2
    rh = (bbox[3] - bbox[1]) + pad_y * 2
    draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(255, 255, 255, 255))
    draw.text(((W - tw) / 2, y), name, font=font, fill=(10, 10, 10))
    return ry + rh

def red_gradient_overlay(size, start_y=650, alpha_max=230):
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for y in range(start_y, size[1]):
        a = int((y - start_y) / (size[1] - start_y) * alpha_max)
        d.rectangle([(0, y), (size[0], y + 1)], fill=(200, 0, 0, a))
    return overlay

def add_f1_logo(img):
    """Draw a small F1-style text logo top-left"""
    d = ImageDraw.Draw(img)
    font = get_font(48, bold=True)
    d.text((40, 40), "F1", font=font, fill=(255, 24, 1))
    d.text((40, 40), "F1", font=font, fill=(255, 255, 255))  # white outline trick
    # Red box around F1
    bbox = d.textbbox((40, 40), "F1", font=font)
    d.rectangle([bbox[0]-6, bbox[1]-4, bbox[2]+6, bbox[3]+4], outline=(255, 24, 1), width=3)
    d.text((40, 40), "F1", font=font, fill=(255, 255, 255))
    return img

# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATE 1 — RACE WINNER
# ══════════════════════════════════════════════════════════════════════════════
def make_winner_post(driver_file, driver_name, race_name, time_str):
    base = load_driver_image(driver_file)
    bw, bh = base.size

    # Crop upper portion and resize
    crop = base.crop((0, 0, bw, int(bh * 0.75)))
    crop = crop.resize((W, 900), Image.LANCZOS)

    canvas = Image.new("RGBA", (W, H), (10, 10, 10, 255))
    canvas.paste(crop, (0, 0), crop)

    # Red gradient from mid
    overlay = red_gradient_overlay((W, H), start_y=550, alpha_max=240)
    canvas = Image.alpha_composite(canvas, overlay)

    # Dark bottom bar
    bar = Image.new("RGBA", (W, 420), (15, 15, 15, 255))
    canvas.paste(bar, (0, H - 420), bar)

    draw = ImageDraw.Draw(canvas)

    # Decorative red stripe
    draw.rectangle([0, H - 425, W, H - 418], fill=(255, 24, 1, 255))

    # Race name
    font_race = get_font(42)
    race_upper = race_name.upper()
    bbox = draw.textbbox((0, 0), race_upper, font=font_race)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, H - 410), race_upper, font=font_race, fill=(200, 200, 200))

    # Driver name badge
    font_name = get_font(62, bold=True)
    draw_name_badge(draw, driver_name, H - 335, font_name)

    # "RACE WINNER" big text
    font_title = get_font(160, bold=True)
    draw_centered_text(draw, "RACE", H - 275, font_title, color=(255, 255, 255))
    draw_centered_text(draw, "WINNER", H - 115, font_title, color=(255, 24, 1))

    # Time label
    if time_str:
        font_time = get_font(44)
        draw_centered_text(draw, f"⏱  {time_str}", H - 42, font_time, color=(180, 180, 180), shadow=False)

    canvas = add_f1_logo(canvas)
    return canvas.convert("RGB")


# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATE 2 — FASTEST LAP
# ══════════════════════════════════════════════════════════════════════════════
def make_fastest_lap_post(driver_file, driver_name, lap_time, race_name):
    base = load_driver_image(driver_file)
    bw, bh = base.size

    crop = base.crop((0, 0, bw, int(bh * 0.75)))
    crop = crop.resize((W, 900), Image.LANCZOS)

    # Purple tint for fastest lap (F1 tradition)
    purple_overlay = Image.new("RGBA", crop.size, (120, 0, 160, 80))
    crop_rgba = crop.convert("RGBA")
    tinted = Image.alpha_composite(crop_rgba, purple_overlay)

    canvas = Image.new("RGBA", (W, H), (10, 5, 20, 255))
    canvas.paste(tinted, (0, 0), tinted)

    # Dark purple gradient
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_ov = ImageDraw.Draw(overlay)
    for y in range(550, H):
        a = int((y - 550) / (H - 550) * 245)
        d_ov.rectangle([(0, y), (W, y + 1)], fill=(40, 0, 80, a))
    canvas = Image.alpha_composite(canvas, overlay)

    # Bottom bar
    bar = Image.new("RGBA", (W, 420), (15, 5, 30, 255))
    canvas.paste(bar, (0, H - 420), bar)

    draw = ImageDraw.Draw(canvas)

    # Purple stripe
    draw.rectangle([0, H - 425, W, H - 418], fill=(180, 0, 220, 255))

    # Race name
    font_race = get_font(42)
    bbox = draw.textbbox((0, 0), race_name.upper(), font=font_race)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, H - 410), race_name.upper(), font=font_race, fill=(200, 180, 220))

    # Driver name badge (purple tones)
    font_name = get_font(62, bold=True)
    bbox2 = draw.textbbox((0, 0), driver_name, font=font_name)
    tw2 = bbox2[2] - bbox2[0]
    pad_x, pad_y = 30, 12
    rx = (W - tw2) / 2 - pad_x
    ry = H - 335 - pad_y
    draw.rectangle([rx, ry, rx + tw2 + pad_x * 2, ry + (bbox2[3]-bbox2[1]) + pad_y*2], fill=(180, 0, 220, 255))
    draw.text(((W - tw2) / 2, H - 335), driver_name, font=font_name, fill=(255, 255, 255))

    # "FASTEST LAP" big text
    font_title = get_font(155, bold=True)
    draw_centered_text(draw, "FASTEST", H - 275, font_title, color=(255, 255, 255))
    draw_centered_text(draw, "LAP", H - 115, font_title, color=(180, 0, 220))

    # Lap time
    if lap_time:
        font_time = get_font(52, bold=True)
        draw_centered_text(draw, lap_time, H - 42, font_time, color=(200, 150, 255), shadow=False)

    canvas = add_f1_logo(canvas)
    return canvas.convert("RGB")


# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATE 3 — PODIUM (3 drivers)
# ══════════════════════════════════════════════════════════════════════════════
def make_podium_post(p1_file, p1_name, p2_file, p2_name, p3_file, p3_name, race_name):
    canvas = Image.new("RGBA", (W, H), (10, 10, 10, 255))

    def place_driver(file, x, y, w, h, tint=None):
        img = load_driver_image(file)
        iw, ih = img.size
        crop = img.crop((0, 0, iw, int(ih * 0.80)))
        crop = crop.resize((w, h), Image.LANCZOS)
        if tint:
            t = Image.new("RGBA", crop.size, tint)
            crop = Image.alpha_composite(crop, t)
        canvas.paste(crop, (x, y), crop)

    # P1 center - larger
    place_driver(p1_file, 190, 30, 700, 820)
    # P2 left
    place_driver(p2_file, -30, 150, 440, 680, tint=(0, 0, 0, 60))
    # P3 right
    place_driver(p3_file, 670, 150, 440, 680, tint=(0, 0, 0, 60))

    # Red gradient bottom
    overlay = red_gradient_overlay((W, H), start_y=580, alpha_max=250)
    canvas = Image.alpha_composite(canvas, overlay)

    # Dark bottom section
    bar = Image.new("RGBA", (W, 470), (12, 12, 12, 255))
    canvas.paste(bar, (0, H - 470), bar)

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, H - 475, W, H - 468], fill=(255, 24, 1, 255))

    # Race name
    font_race = get_font(40)
    race_up = race_name.upper()
    bbox = draw.textbbox((0, 0), race_up, font=font_race)
    draw.text(((W - (bbox[2]-bbox[0])) / 2, H - 462), race_up, font=font_race, fill=(200, 200, 200))

    # PODIUM title
    font_title = get_font(175, bold=True)
    draw_centered_text(draw, "PODIUM", H - 390, font_title, color=(255, 24, 1))

    # Three name badges side by side
    font_pos = get_font(52, bold=True)
    font_nm = get_font(38, bold=True)

    positions = [
        (1, p1_name, W // 2),
        (2, p2_name, W // 4),
        (3, p3_name, 3 * W // 4),
    ]

    pos_colors = {1: (255, 215, 0), 2: (192, 192, 192), 3: (205, 127, 50)}

    for pos, name, cx in positions:
        # Number circle
        r = 38
        draw.ellipse([cx - r, H - 230 - r, cx + r, H - 230 + r], fill=pos_colors[pos])
        nb = draw.textbbox((0, 0), str(pos), font=font_pos)
        nw = nb[2] - nb[0]
        draw.text((cx - nw // 2, H - 230 - (nb[3]-nb[1])//2 - 4), str(pos), font=font_pos, fill=(10, 10, 10))

        # Name
        nb2 = draw.textbbox((0, 0), name, font=font_nm)
        nw2 = nb2[2] - nb2[0]
        draw.rectangle(
            [cx - nw2//2 - 16, H - 175 - 10, cx + nw2//2 + 16, H - 175 + (nb2[3]-nb2[1]) + 10],
            fill=(255, 255, 255, 230)
        )
        draw.text((cx - nw2 // 2, H - 175), name, font=font_nm, fill=(10, 10, 10))

    canvas = add_f1_logo(canvas)
    return canvas.convert("RGB")


# ─── UI ───────────────────────────────────────────────────────────────────────
drivers = get_drivers()

if not drivers:
    st.error(f"⚠️  Nessun file trovato nella cartella **{DRIVER_FOLDER}/**. Assicurati che esista e contenga immagini .avif / .png.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🏆  Race Winner", "⚡  Fastest Lap", "🥇🥈🥉  Podium"])

# ── TAB 1: WINNER ─────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Race Winner")
    col1, col2 = st.columns(2)
    with col1:
        w_driver = st.selectbox("Pilota", drivers, key="w_driver")
        w_name = st.text_input("Nome (sovrascrive auto)", clean_driver_name(w_driver), key="w_name")
    with col2:
        w_race = st.text_input("Nome Gara", "BAHRAIN GRAND PRIX", key="w_race")
        w_time = st.text_input("Tempo gara (opz.)", "1:31:44.742", key="w_time")

    if st.button("Genera Winner Post", key="gen_winner"):
        with st.spinner("Generando..."):
            img = make_winner_post(w_driver, w_name, w_race, w_time)
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("⬇️  Scarica PNG", buf.getvalue(),
                               file_name=f"winner_{w_name.replace(' ','_')}.png", mime="image/png")

# ── TAB 2: FASTEST LAP ────────────────────────────────────────────────────────
with tab2:
    st.subheader("Fastest Lap")
    col1, col2 = st.columns(2)
    with col1:
        f_driver = st.selectbox("Pilota", drivers, key="f_driver")
        f_name = st.text_input("Nome", clean_driver_name(f_driver), key="f_name")
    with col2:
        f_race = st.text_input("Nome Gara", "BAHRAIN GRAND PRIX", key="f_race")
        f_time = st.text_input("Tempo giro", "1'32\"847", key="f_time")

    if st.button("Genera Fastest Lap Post", key="gen_fast"):
        with st.spinner("Generando..."):
            img = make_fastest_lap_post(f_driver, f_name, f_time, f_race)
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("⬇️  Scarica PNG", buf.getvalue(),
                               file_name=f"fastest_{f_name.replace(' ','_')}.png", mime="image/png")

# ── TAB 3: PODIUM ─────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Podium — 3 Piloti")
    p_race = st.text_input("Nome Gara", "BAHRAIN GRAND PRIX", key="p_race")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🥇 P1**")
        p1_driver = st.selectbox("Pilota P1", drivers, key="p1_d")
        p1_name = st.text_input("Nome P1", clean_driver_name(p1_driver), key="p1_n")
    with col2:
        st.markdown("**🥈 P2**")
        p2_driver = st.selectbox("Pilota P2", drivers, index=min(1, len(drivers)-1), key="p2_d")
        p2_name = st.text_input("Nome P2", clean_driver_name(p2_driver), key="p2_n")
    with col3:
        st.markdown("**🥉 P3**")
        p3_driver = st.selectbox("Pilota P3", drivers, index=min(2, len(drivers)-1), key="p3_d")
        p3_name = st.text_input("Nome P3", clean_driver_name(p3_driver), key="p3_n")

    if st.button("Genera Podium Post", key="gen_podium"):
        with st.spinner("Generando..."):
            img = make_podium_post(p1_driver, p1_name, p2_driver, p2_name, p3_driver, p3_name, p_race)
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("⬇️  Scarica PNG", buf.getvalue(),
                               file_name=f"podium_{p_race.replace(' ','_')}.png", mime="image/png")
