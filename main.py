import os
from flask import Flask, request
import telebot
from telebot import types
from datetime import datetime
import random

# ================== Настройки ==================
TOKEN = os.getenv("BOT_TOKEN")  # Токен з Render Secrets
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================== База ==================
banned_users = set()
rewards_db = {}  # {user_id: [список нагород]}
admin_groups = set()  # групи, куди доданий бот

# ================== Нагороди ==================
ALL_REWARDS = [
    "🏆 «Легендарный герой»",
    "🎖 «Мегамозг недели»",
    "⭐ «Лучший пользователь суток»",
    "🔥 «Самый активный»",
    "💎 «Алмазный участник»",
    "👑 «Король чата»",
    "⚡ «Император активности»",
    "🎯 «Мастер точности»",
    "💼 «Лучший работяга»",
    "🐺 «Волк-одиночка»",
    "🐉 «Драконий ранг»",
    "📢 «Оратор месяца»",
    "💡 «Идея года»",
    "📊 «Статист легенды»",
    "🚀 «Сверхактивный»",
    "🔱 «Элитный участник»",
    "🌟 «Секретная звезда»",
    "🥇 «Чемпион чата»",
    "🕹 «Игровой мастер»",
    "🛡 «Защитник»",
    "🌈 «Радуга дружбы»",
    "💌 «Посланник любви»"
]

# ================== Главное меню ==================
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🆕 Новые обращения", "💬 Поддержка", "🎁 Совет дня", "🏆 Достижения")
    return kb

# ================== Старое приветствие ==================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(msg.chat.id, 
                     "Привет! Я бот поддержки. Выбирай кнопку ниже:", 
                     reply_markup=main_menu())

# ================== Новые обращения ==================
@bot.message_handler(func=lambda m: m.text == "🆕 Новые обращения")
def new_request(msg):
    bot.send_message(msg.chat.id, "Напиши сообщение админам:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Главное меню"))

# ================== Поддержка ==================
@bot.message_handler(func=lambda m: m.text == "💬 Поддержка")
def support(msg):
    bot.send_message(msg.chat.id, "Напиши ваш вопрос для поддержки:", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Главное меню"))

# ================== Совет дня ==================
@bot.message_handler(func=lambda m: m.text == "🎁 Совет дня")
def advice(msg):
    advices = [
        "💡 Совет: улыбайся чаще!",
        "💡 Совет: пей воду и отдыхай!",
        "💡 Совет: помогай друзьям!",
        "💡 Совет: маленькие шаги ведут к большим результатам!",
        "💡 Совет: учись новому каждый день!"
    ]
    bot.send_message(msg.chat.id, random.choice(advices), reply_markup=main_menu())

# ================== Достижения ==================
@bot.message_handler(func=lambda m: m.text == "🏆 Достижения")
def achievements(msg):
    user_id = msg.from_user.id
    user_rewards = rewards_db.get(user_id, [])
    if not user_rewards:
        bot.send_message(msg.chat.id, "У вас пока нет достижений.", reply_markup=main_menu())
        return
    text = "Ваши достижения:\n" + "\n".join(user_rewards)
    bot.send_message(msg.chat.id, text, reply_markup=main_menu())

# ================== Бан/Разбан ==================
@bot.message_handler(func=lambda m: m.text.lower() in ["бан", "разбан"])
def ban_unban(msg):
    if not msg.reply_to_message:
        bot.send_message(msg.chat.id, "Ответь на сообщение пользователя для команды.")
        return
    user_id = msg.reply_to_message.from_user.id
    if msg.text.lower() == "бан":
        banned_users.add(user_id)
        bot.send_message(msg.chat.id, f"Пользователь {user_id} забанен.")
    else:
        banned_users.discard(user_id)
        bot.send_message(msg.chat.id, f"Пользователь {user_id} разбанен.")

# ================== Список забаненных ==================
@bot.message_handler(func=lambda m: m.text.lower() == "забаненные")
def banned_list(msg):
    if not banned_users:
        bot.send_message(msg.chat.id, "Список пуст.")
        return
    text = "\n".join(str(u) for u in banned_users)
    bot.send_message(msg.chat.id, f"Забаненные:\n{text}")

# ================== Пересылка сообщений в админ-группы ==================
@bot.message_handler(func=lambda m: True)
def forward_to_admins(msg):
    if msg.from_user.id in banned_users:
        return
    text = f"📩 ПОДДЕРЖКА!!!\nОт: @{msg.from_user.username} (ID {msg.from_user.id})\n\n«{msg.text}»"
    for chat_id in admin_groups:
        try:
            bot.send_message(chat_id, text)
        except:
            pass

# ================== Награды ==================
@bot.message_handler(func=lambda m: m.text.lower() == "награда")
def give_reward(msg):
    user_id = msg.from_user.id
    reward = random.choice(ALL_REWARDS)
    rewards_db.setdefault(user_id, []).append(reward)
    bot.send_message(msg.chat.id, f"🎉 Вы получили награду:\n{reward}")

# ================== Webhook ==================
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def home():
    return "Бот работает ✅"

# ================== Добавление бота в группы ==================
@bot.chat_member_handler()
def added_to_group(chat_member_updated):
    if chat_member_updated.new_chat_member.user.id == bot.get_me().id:
        admin_groups.add(chat_member_updated.chat.id)

# ================== Запуск ==================
if __name__ == "__main__":
    # удаляем старый webhook
    bot.remove_webhook()
    print("Webhook очищен")
    # запуск Flask через Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8800)))
