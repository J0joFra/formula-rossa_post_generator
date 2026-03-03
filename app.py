import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pillow_avif
import os
import io

st.set_page_config(layout="centered")

st.title("🏎 Formula Rossa Post Generator")

DRIVER_FOLDER = "Drivers"

# === LISTA DRIVER ===
driver_files = [f for f in os.listdir(DRIVER_FOLDER) if f.endswith(".avif")]

selected_driver = st.selectbox("Seleziona Pilota", driver_files)

lap_time = st.text_input("Tempo", "1'35\"67")

generate = st.button("Genera Post")

if generate:

    # === CARICA IMMAGINE ===
    image_path = os.path.join(DRIVER_FOLDER, selected_driver)
    base = Image.open(image_path).convert("RGB")

    # === CROP SOLO META' SUPERIORE ===
    width, height = base.size
    cropped = base.crop((0, 0, width, height // 2))

    # === RIDIMENSIONA PER IG ===
    cropped = cropped.resize((1080, 1350))

    # === OVERLAY ROSSO GRADIENTE ===
    overlay = Image.new("RGBA", cropped.size, (255, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    for y in range(800, 1350):
        alpha = int((y - 800) / 550 * 220)
        draw_overlay.rectangle([(0, y), (1080, y+1)], fill=(255, 0, 0, alpha))

    combined = Image.alpha_composite(cropped.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(combined)

    # === FONT ===
    try:
        font_big = ImageFont.truetype("arial.ttf", 200)
        font_small = ImageFont.truetype("arial.ttf", 60)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # === ESTRAI NOME DAL FILE ===
    driver_clean = selected_driver.replace("2026", "")
    driver_clean = driver_clean.replace("01right.avif", "")
    driver_name = driver_clean.upper()

    # === BOX NOME ===
    text_width = draw.textlength(driver_name, font=font_small)
    box_x = (1080 - text_width) / 2 - 20
    box_y = 780
    box_w = text_width + 40
    box_h = 80

    draw.rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        fill="white"
    )

    draw.text(
        ((1080 - text_width) / 2, box_y + 10),
        driver_name,
        fill="black",
        font=font_small
    )

    # === TEMPO GRANDE CENTRATO ===
    time_width = draw.textlength(lap_time, font=font_big)

    draw.text(
        ((1080 - time_width) / 2, 950),
        lap_time,
        fill="white",
        font=font_big
    )

    st.image(combined)

    # === DOWNLOAD ===
    buf = io.BytesIO()
    combined.convert("RGB").save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Scarica Post",
        data=byte_im,
        file_name=f"{driver_name}_post.png",
        mime="image/png"
    )
