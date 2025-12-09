import os
from flask import Flask, request
import telebot
from telebot import types
from datetime import datetime
from random import choice

# ====== Настройки ======
BOT_TOKEN = os.getenv("BOT_TOKEN")  # На Render додай BOT_TOKEN в секрети
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

OWNER_ID = 1470389051  # твій Telegram ID

# ====== База данных ======
reviews_db = {"admins": {}, "pending": {}}
banned = set()
rewards = {}

# ====== Главное меню ======
def main_menu_markup():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Новые обращения", "Поддержка", "Совет дня", "Достижения")
    return kb

# ====== Старт ======
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот поддержки 🖤",
        reply_markup=main_menu_markup()
    )

# ====== Бан/Разбан (для админов) ======
@bot.message_handler(func=lambda m: m.text.lower() in ["бан", "разбан"])
def manage_ban(message):
    if message.from_user.id != OWNER_ID:
        bot.send_message(message.chat.id, "⛔️ Нет доступа.")
        return
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "Ответь на сообщение пользователя.")
        return
    user_id = message.reply_to_message.from_user.id
    if message.text.lower() == "бан":
        banned.add(user_id)
        bot.send_message(message.chat.id, f"Пользователь {user_id} забанен.")
    else:
        banned.discard(user_id)
        bot.send_message(message.chat.id, f"Пользователь {user_id} разбанен.")

# ====== Награды ======
ALL_REWARDS = [
    "🏆 «Легендарный герой»", "🎖 «Мегамозг недели»", "⭐ «Лучший пользователь суток»",
    "🔥 «Самый активный»", "💎 «Алмазный участник»", "👑 «Король чата»",
    "⚡ «Император активности»", "🎯 «Мастер точности»", "💼 «Лучший работяга»"
]

@bot.message_handler(func=lambda m: m.text.lower() == "награда")
def give_reward(message):
    user_id = message.from_user.id
    reward = choice(ALL_REWARDS)
    rewards[user_id] = reward
    bot.send_message(message.chat.id, f"🎉 Вы получили награду:\n{reward}")

# ====== Пересылка сообщений в админ-группу ======
admin_groups = set()  # Render сам підкине групу після додавання бота

@bot.message_handler(func=lambda m: True)
def redirect_to_admins(message):
    if message.from_user.id in banned:
        return
    text = f"📩 ПОДДЕРЖКА!!!\nОт: @{message.from_user.username}\nID: {message.from_user.id}\n\n«{message.text}»"
    for chat_id in admin_groups:
        try:
            bot.send_message(chat_id, text)
        except:
            pass

# ====== Webhook для Render ======
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def home():
    return "Бот работает ✅"

# ====== Запуск (только webhook) ======
if __name__ == "__main__":
    bot.remove_webhook()
    print("Webhook удален")
    # Render сам подкине порт
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
