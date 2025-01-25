from loader import bot,dp
from aiogram import types
from typing import Union
import sqlite3
from aiogram.types import  InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramAPIError

from aiogram.types import ChatJoinRequest

from handlers.users.start import show_referral_info, show_top_referrers
from handlers.users.help import help_bot

from middlewares.user_commands import user_commands


DATABASE_FILE = "bot.db"

def db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    return conn


def create_join_requests_table():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS join_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        chat_id INTEGER NOT NULL,
        request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        comments TEXT DEFAULT NULL
    )
    """)
    conn.commit()
    conn.close()

# Call this function once during initialization
create_join_requests_table()

def save_join_request(user_id: int, chat_id: int):
    """
    Foydalanuvchining kanalga qo'shilish uchun so'rov yuborganligini saqlash.
    """
    conn = db_connection()
    cursor = conn.cursor()

    # Foydalanuvchining mavjudligini tekshirish
    cursor.execute("""
        SELECT id FROM join_requests
        WHERE user_id = ? AND chat_id = ?
    """, (user_id, chat_id))
    existing_request = cursor.fetchone()

    if not existing_request:
        # Yangi yozuv qo'shish
        cursor.execute("""
            INSERT INTO join_requests (user_id, chat_id)
            VALUES (?, ?)
        """, (user_id, chat_id))
    
    conn.commit()
    conn.close()


def check_user_in_requests(user_id: int, chat_id: int) -> bool:
    """
    Foydalanuvchining ma'lum bir kanalga qo'shilish so'rovi mavjudligini tekshirish.
    """
    conn = db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM join_requests
        WHERE user_id = ? AND chat_id = ?
    """, (user_id, chat_id))
    result = cursor.fetchone()
    conn.close()

    return result is not None




def get_channels():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channels")
    channels = cursor.fetchall()
    conn.close()
    return channels


async def is_invite_link_valid(chat_id: int) -> bool:
    try:
        member_count = await bot.get_chat_member_count(chat_id)
        return True
    except TelegramAPIError as e:
        return False

async def update_invite_link_in_db(chat_id: int, new_invite_link: str):
    query = """
    UPDATE channels
    SET invite_link = %s
    WHERE chat_id = %s
    """
    conn = db_connection()
    db = conn.cursor()
    await db.execute(query, (new_invite_link, chat_id))


async def get_valid_invite_link(chat_id: int, current_invite_link: str, invite_required: bool) -> str:
    is_valid = await is_invite_link_valid(chat_id)
    
    if not is_valid:
        try:
            if invite_required:
                new_invite_link = await bot.create_chat_invite_link(
                    chat_id=chat_id,
                    creates_join_request=True
                )
            else:
                new_invite_link = await bot.create_chat_invite_link(
                    chat_id=chat_id,
                    creates_join_request=False
                )
            await update_invite_link_in_db(chat_id, new_invite_link.invite_link)
            
            return new_invite_link.invite_link
        except Exception as e:
            return current_invite_link
    else:
        return current_invite_link




async def check_sub(user_id):
    channels = get_channels()

    for channel in channels:
        chat_id = channel[3]

        if check_user_in_requests(user_id, chat_id):
            continue

        chat_member = await bot.get_chat_member(chat_id, user_id)

        if chat_member.status not in ["creator", "administrator", "member", 'restricted']:
            return False
        
    return True


async def joinchat(user_id):
    channels = get_channels()
    inline_keyboard = InlineKeyboardBuilder()
    uns = False

    for channel in channels:
        chat_id, chat_username, invite_link, invite_required = channel[3], channel[1], channel[6], channel[-1]

        invite_link = await get_valid_invite_link(chat_id, invite_link,invite_required)

        if check_user_in_requests(user_id, chat_id):
            continue

        chat_member = await bot.get_chat_member(chat_id, user_id)

        if chat_member.status not in ["creator", "administrator", "member"]:
            if invite_required and chat_member.status == "restricted":
                continue
            button = InlineKeyboardButton(text=f"➕ Obuna bo'lish", url=str(invite_link))
            uns = True
            inline_keyboard.add(button)

    check_button = InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="check_subscriptions")
    inline_keyboard.add(check_button)
    inline_keyboard.adjust(1)

    if uns:
        await bot.send_message(user_id, "Iltimos, quyidagi kanallarimizga obuna bo'ling, keyin botni ishlatishingiz mumkin.", reply_markup=inline_keyboard.as_markup())
        return False
    else:
        return True
    



@dp.callback_query(lambda query: query.data.startswith("check_subscriptions"))
async def check_subscription(callback_query: types.CallbackQuery):
    is_subscribed = await check_sub(callback_query.from_user.id)
    user_id = callback_query.from_user.id
    
    if is_subscribed:
        await bot.send_message(chat_id=callback_query.message.chat.id, text="Juda siz endi botni ishlatishingiz mumkin")
        await bot.delete_message(callback_query.message.chat.id, message_id=callback_query.message.message_id)
        
        if user_commands:
            # Create a copy of the dictionary to avoid modifying it while iterating
            for user_id in list(user_commands.keys()):
                command_or_message = user_commands[user_id]
                await process_user_command(command_or_message, callback_query.message)

                # Clear after processing
                del user_commands[user_id]
    else:
        await callback_query.answer("Iltimos, quyidagi kanallarimizga obuna bo'ling, keyin botni ishlatishingiz mumkin", show_alert=True)


async def process_user_command(command_or_message: str, message: types.Message):
    if command_or_message == '/referal':
        await show_referral_info(message)
    elif command_or_message == '/topreferals':
        await show_top_referrers(message)


@dp.chat_join_request()
async def handle_join_request(join_request: ChatJoinRequest):
    chat_id = join_request.chat.id
    user_id = join_request.from_user.id
    save_join_request(user_id, chat_id)

    # await bot.send_message(
    #     user_id,
    #     "Sizning so'rovingiz qabul qilindi. Iltimos, admin tomonidan tasdiqlashni kuting."
    # )



