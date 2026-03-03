import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(layout="centered")

st.title("🏎 F1 Post Generator")

uploaded_file = st.file_uploader("Carica immagine pilota", type=["png", "jpg", "jpeg"])
driver_name = st.text_input("Nome pilota", "CHARLES LECLERC")
lap_time = st.text_input("Tempo", "1'35\"67")

generate = st.button("Genera Post")

if uploaded_file and generate:
    # Apri immagine
    base = Image.open(uploaded_file).convert("RGB")
    base = base.resize((1080, 1350))

    # Overlay rosso gradiente
    overlay = Image.new("RGBA", base.size, (255, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    for y in range(800, 1350):
        alpha = int((y - 800) / 550 * 220)
        draw_overlay.rectangle([(0, y), (1080, y+1)], fill=(255, 0, 0, alpha))

    combined = Image.alpha_composite(base.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(combined)

    # Font (usa uno di sistema se non hai file font)
    try:
        font_big = ImageFont.truetype("arial.ttf", 200)
        font_small = ImageFont.truetype("arial.ttf", 60)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Box nome pilota
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

    # Tempo gigante centrato
    time_width = draw.textlength(lap_time, font=font_big)

    draw.text(
        ((1080 - time_width) / 2, 950),
        lap_time,
        fill="white",
        font=font_big
    )

    st.image(combined)

    # Download
    buf = io.BytesIO()
    combined.convert("RGB").save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Scarica immagine",
        data=byte_im,
        file_name="f1_post.png",
        mime="image/png"
    )
