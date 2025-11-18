import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

# Logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN") 

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# Create Updater and Dispatcher
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Handle /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("أهلاً دكتور محمد 👋 أنا مساعدك الطبي الذكي، كيف أساعدك؟")

# Handle user messages
def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a medical AI assistant."},
            {"role": "user", "content": user_text}
        ]
    )

    reply = response["choices"][0]["message"]["content"]
    update.message.reply_text(reply)

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update_data = request.get_json(force=True)
    update = Update.de_json(update_data, bot)
    dispatcher.process_update(update)
    return "OK", 200

# Home route
@app.route("/")
def home():
    return "AI Hospital Assistant is running!"

# Run locally (Render ignores this)
if __name__ == "__main__":
    updater.start_polling()
    app.run(host="0.0.0.0", port=8080)
