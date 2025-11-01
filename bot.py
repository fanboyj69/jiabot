import os
import json
import random
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
ALLOWED_GROUP_ID = int(os.getenv("ALLOWED_GROUP_ID"))
API_URL = os.getenv("API_URL")
WALLPAPER_API_URL = os.getenv("WALLPAPER_API_URL")

# Load videos from data.json
with open("./data.json", "r", encoding="utf-8") as f:
    videos = json.load(f)

# === Helper functions ===
def get_video_url():
    video = random.choice(videos)
    video_id = video.get("v")
    if not str(video_id).endswith(".mp4"):
        video_id = f"{video_id}.mp4"
    url = f"{API_URL}{video_id}"
    print(f"🎬 Selected video URL: {url}")
    return url

def get_wallpaper_url():
    wallpaper_id = random.randint(1, 30999)
    url = f"{WALLPAPER_API_URL}{wallpaper_id}.jpg"
    print(f"🖼️ Selected wallpaper URL: {url}")
    return url

def is_allowed_group(update: Update):
    return update.effective_chat.id == ALLOWED_GROUP_ID

# === Command Handlers ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_group(update):
        return
    await update.message.reply_text("👋 Hello! Send /video for videos or /wallpaper for wallpapers.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_group(update):
        return
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Greet the bot\n"
        "/video - Get a random video\n"
        "/wallpaper - Get a random wallpaper"
    )

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_group(update):
        return
    video_url = get_video_url()
    try:
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=video_url,
            caption="Video by @rolexpmv",
            reply_to_message_id=update.message.message_id
        )
    except Exception as e:
        print(f"❌ Error sending video: {e}")
        await update.message.reply_text("⚠️ Couldn't send the video. Maybe it's too large or unavailable.")

async def wallpaper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed_group(update):
        return
    wallpaper_url = get_wallpaper_url()
    try:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=wallpaper_url,
            caption="Wallpaper by @rolexpmv",
            reply_to_message_id=update.message.message_id
        )
    except Exception as e:
        print(f"❌ Error sending wallpaper: {e}")
        await update.message.reply_text("⚠️ Couldn't send the wallpaper right now.")

# === Flask app for webhook ===
app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Register handlers
dispatcher.add_handler(CommandHandler("start", start_command))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("video", video_command))
dispatcher.add_handler(CommandHandler("wallpaper", wallpaper_command))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running!"

# === Run Flask app (PythonAnywhere WSGI will call this) ===
if __name__ == "__main__":
    app.run(port=8443)
