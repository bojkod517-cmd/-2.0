import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import os

TOKEN = os.getenv("7951787769:AAEtwsM7_wxuSed770XAShIyZ5GRzne9tFs")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- База пользователей ---
banned = set()
rewards = {}

# --- Список груп, куда добавлен бот ---
admin_groups = set()


# Когда бот добавлен в группу
@dp.chat_member()
async def bot_added(event):
    if event.new_chat_member and event.new_chat_member.user.id == (await bot.get_me()).id:
        admin_groups.add(event.chat.id)


# Бан
@dp.message(F.text.lower() == "бан")
async def ban_user(msg: Message):
    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
        banned.add(user_id)
        await msg.answer(f"Пользователь {user_id} забанен.")
    else:
        await msg.answer("Ответь на сообщение пользователя, которого нужно забанить.")


# Разбан
@dp.message(F.text.lower() == "разбан")
async def unban_user(msg: Message):
    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
        banned.discard(user_id)
        await msg.answer(f"Пользователь {user_id} разбанен.")
    else:
        await msg.answer("Ответь на сообщение пользователя, которого нужно разбанить.")


# Список забаненных
@dp.message(F.text.lower() == "забаненные")
async def list_banned(msg: Message):
    if not banned:
        await msg.answer("Список пуст.")
    else:
        text = "\n".join(str(u) for u in banned)
        await msg.answer(f"Забаненные:\n{text}")


# Награды — много разных
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
    "🔱 «Элитный участник»"
]


@dp.message(F.text.lower() == "награда")
async def give_reward(msg: Message):
    user_id = msg.from_user.id
    from random import choice
    reward = choice(ALL_REWARDS)

    rewards[user_id] = reward

    await msg.answer(f"🎉 Вы получили награду:\n{reward}")


# Пересылка обращений в админ-группы
@dp.message()
async def redirect(msg: Message):
    if msg.from_user.id in banned:
        return  # игнорим забаненных

    text = f"📩 ПОДДЕРЖКА!!!\nОт: @{msg.from_user.username}\nID: {msg.from_user.id}\n\n«{msg.text}»"

    for chat_id in admin_groups:
        try:
            await bot.send_message(chat_id, text)
        except:
            pass


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
