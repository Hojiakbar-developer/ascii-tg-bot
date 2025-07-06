import os
from dotenv import load_dotenv

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,  # 👈 Bu yerda bo‘lishi shart
    ContextTypes,
    filters,
)

# Pro ASCII belgilar — realistik o‘tish uchun
ASCII_CHARS = list("█@%#*+=-:. ")  # Chapdan o‘ngga — qora → oq

# Rasmni o'lchamini moslashtirish
def resize_image(image, new_width=200):
    width, height = image.size
    ratio = height / width / 1.9
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height))

# Kulrangga aylantirish + kontrastni kuchaytirish
def grayify(image):
    image = image.convert("L")
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)  # Kontrastni kuchaytirish
    return image

# Piksellarni ASCII belgilariga aylantirish
def pixels_to_ascii(image):
    pixels = image.getdata()
    scale = 256 / len(ASCII_CHARS)
    ascii_str = "".join(ASCII_CHARS[int(pixel / scale)] for pixel in pixels)
    return ascii_str

# Rasmni ASCII matnga aylantirish
def convert_image_to_ascii(image_path):
    try:
        image = Image.open(image_path)
    except Exception as e:
        return None, f"Could not open image: {e}"

    image = resize_image(image)
    image = grayify(image)
    ascii_str = pixels_to_ascii(image)

    pixel_count = len(ascii_str)
    ascii_image = "\n".join(ascii_str[i:(i + 200)] for i in range(0, pixel_count, 200))
    return ascii_image, None

# ASCII matnni rasmga aylantirish
def ascii_to_image(ascii_text, output_path, font_path="C:/Windows/Fonts/consola.ttf"):
    lines = ascii_text.split("\n")
    font_size = 13
    font = ImageFont.truetype(font_path, font_size)

    max_width = max([font.getlength(line) for line in lines]) + 20
    height = font_size * len(lines) + 20

    image = Image.new("L", (int(max_width), height), color=255)
    draw = ImageDraw.Draw(image)

    y = 0
    for line in lines:
        draw.text((10, y), line, font=font, fill=0)
        y += font_size

    image.save(output_path)

# Start buyrug'i funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello, welcome to ASCII art.")
    await update.message.reply_text("📷 Send me a picture and I'll make ASCII art.")

# Telegram photo handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ image received. Converting to ASCII art...")

    user_id = update.message.from_user.id
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    img_path = f"temp_{user_id}.jpg"
    output_img = f"ascii_{user_id}.png"
    await file.download_to_drive(img_path)

    ascii_art, error = convert_image_to_ascii(img_path)
    if error:
        await update.message.reply_text(error)
        return

    ascii_to_image(ascii_art, output_img)

    with open(output_img, "rb") as img_file:
        await update.message.reply_photo(photo=img_file, caption="🎨 you're ASCII art is ready!")

    os.remove(img_path)
    os.remove(output_img)

# Botni ishga tushirish
if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))  # ✅ start komandasi qo‘shildi
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("✅ Pro ASCII Bot ishga tushdi!")
    app.run_polling(on_startup=on_startup)

