import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

# Logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# Handle /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحباً دكتور محمد 👋، أنا مساعدك الذكي في المستشفى!")

# Handle chat messages
def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a medical AI assistant."},
            {"role": "user", "content": user_text}
        ]
    )

    reply = response["choices"][0]["message"]["content"]
    update.message.reply_text(reply)

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Create dispatcher
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.route("/")
def home():
    return "AI Hospital Assistant is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
