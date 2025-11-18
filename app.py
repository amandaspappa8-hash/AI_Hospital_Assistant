import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Telegram bot application
tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً دكتور محمد 👋، أنا مساعدك الذكي في المستشفى!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a medical AI assistant."},
            {"role": "user", "content": user_text}
        ]
    )

    reply = response["choices"][0]["message"]["content"]
    await update.message.reply_text(reply)

tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data)
    tg_app.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/")
def home():
    return "AI Hospital Assistant is running!"

if __name__ == "__main__":
    tg_app.run_polling()
    app.run(host="0.0.0.0", port=8080)
