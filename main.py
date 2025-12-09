import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ChatMemberUpdated
import os

# --- ВАЖЛИВО ---
# УСТАНОВИ В RENDER/RAILWAY переменную: BOT_TOKEN = твой токен
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Базы
banned = set()
rewards = {}
admin_groups = set()

# Коли бот доданий в групу
@dp.chat_member(ChatMemberUpdated)
async def bot_added(event: ChatMemberUpdated):
    me = await bot.get_me()
    if event.new_chat_member.user.id == me.id:
        admin_groups.add(event.chat.id)


# --- БАН ---
@dp.message(F.text.lower() == "бан")
async def ban_user(msg: Message):
    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
        banned.add(user_id)
        await msg.answer(f"Пользователь {user_id} забанен.")
    else:
        await msg.answer("Ответь на сообщение пользователя, которого нужно забанить.")


# --- РАЗБАН ---
@dp.message(F.text.lower() == "разбан")
async def unban_user(msg: Message):
    if msg.reply_to_message:
        user_id = msg.reply_to_message.from_user.id
        banned.discard(user_id)
        await msg.answer(f"Пользователь {user_id} разбанен.")
    else:
        await msg.answer("Ответь на сообщение пользователя, которого нужно разбанить.")


# --- СПИСОК БАННЕД ---
@dp.message(F.text.lower() == "забаненные")
async def list_banned(msg: Message):
    if not banned:
        await msg.answer("Список пуст.")
    else:
        text = "\n".join(str(i) for i in banned)
        await msg.answer("Забаненные:\n" + text)


# --- НАГРАДА ---
ALL_REWARDS = [
    "🏆 «Легендарный герой»", "🎖 «Мегамозг недели»",
    "⭐ «Лучший пользователь суток»", "🔥 «Самый активный»",
    "💎 «Алмазный участник»", "👑 «Король чата»",
    "⚡ «Император активности»", "🎯 «Мастер точности»",
    "💼 «Лучший работяга»", "🐺 «Волк-одиночка»",
    "🐉 «Драконий ранг»", "📢 «Оратор месяца»",
    "💡 «Идея года»", "📊 «Статист легенды»",
    "🚀 «Сверхактивный»", "🔱 «Элитный участник»"
]

@dp.message(F.text.lower() == "награда")
async def give_reward(msg: Message):
    from random import choice
    reward = choice(ALL_REWARDS)
    rewards[msg.from_user.id] = reward
    await msg.answer(f"🎉 Вы получили награду:\n{reward}")


# --- ПЕРЕСЫЛКА ВСЕХ СООБЩЕНИЙ В АДМИН-ГРУППЫ ---
@dp.message()
async def redirect(msg: Message):
    if msg.from_user.id in banned:
        return

    text = (
        "📩 ПОДДЕРЖКА!!!\n"
        f"От: @{msg.from_user.username}\n"
        f"ID: {msg.from_user.id}\n\n"
        f"«{msg.text}»"
    )

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
