from loader import dp,bot
from aiogram import types,html,F
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sqlite3,json
from datetime import datetime
from aiogram.types import  InlineKeyboardButton,InlineKeyboardMarkup
from filters import IsAdmin
from data.config import ADMINS, USERS_CHANNEL

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()




cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(30) NULL,
    full_name TEXT,
    telegram_id BIGINTEGER UNIQUE,
    lang_code VARCHAR(10) NULL,
    registration_date TEXT,
    referred_by INTEGER,
    referral_code VARCHAR(20) NULL UNIQUE,
    invited_users TEXT DEFAULT '[]',
    FOREIGN KEY (referred_by) REFERENCES users (id)
)
''')
conn.commit()

def generate_referral_code():
    """Tasodifiy referal kod yaratish."""
    import uuid
    return f"r_{uuid.uuid4().hex[:8]}"


def get_user_by_referral_code(referral_code):
    cursor.execute('''
        SELECT * FROM users WHERE referral_code = ?
    ''', (referral_code,))
    return cursor.fetchone()

def add_user(telegram_id, username, full_name, registration_date, referred_by=None):
    referral_code = generate_referral_code()
    invited_users = json.dumps([])  # Taklif qilingan do'stlar ro'yxati
    cursor.execute('''
        INSERT INTO users (telegram_id, username, full_name, registration_date, referred_by, invited_users, referral_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (telegram_id, username, full_name, registration_date, referred_by, invited_users, referral_code))
    conn.commit()

    # Agar referred_by mavjud bo'lsa, taklif qilgan foydalanuvchining invited_users maydonini yangilaymiz
    if referred_by:
        cursor.execute('SELECT invited_users FROM users WHERE id = ?', (referred_by,))
        result = cursor.fetchone()
        if result:
            invited_list = json.loads(result[0])  # Taklif qilingan foydalanuvchilar ro'yxati
            invited_list.append(telegram_id)  # Yangi foydalanuvchini qo'shamiz
            updated_invited_users = json.dumps(invited_list)
            cursor.execute('UPDATE users SET invited_users = ? WHERE id = ?', (updated_invited_users, referred_by))
            conn.commit()


async def is_user_registered(telegram_id):
    cursor.execute('''
        SELECT telegram_id FROM users WHERE telegram_id=?
    ''', (telegram_id,))
    result = cursor.fetchone()
    return result is not None



@dp.message(F.text, ~IsAdmin())
async def start_bot(message: types.Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name[:20]  # Maksimal uzunlik
    username = message.from_user.username
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    is_premium = message.from_user.is_premium

    if not await is_user_registered(telegram_id):
        add_user(telegram_id, username, full_name, registration_date)  # Agar foydalanuvchi ro'yxatda bo'lmasa
        try:
            await bot.send_message(
                chat_id=USERS_CHANNEL,
                text=(
                    f"New 👤: {html.escape(full_name)}\n"
                    f"Username📩: {html.code(username)}\n"
                    f"Telegram 🆔: {html.code(str(telegram_id))}\n"
                    f"Reg 📆: {registration_date}\n"
                    f"Premium🤑: {is_premium}"
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="Profile", url=f"tg://user?id={telegram_id}")]]
                ),
            )
        except:
            for admin_id in ADMINS:
                try:
                    await bot.send_message(
                        chat_id=admin_id,
                        text=(
                            f"New 👤: {html.escape(full_name)}\n"
                            f"Username📩: {html.code(username)}\n"
                            f"Telegram 🆔: {html.code(str(telegram_id))}\n"
                            f"Reg 📆: {registration_date}\n"
                            f"Premium🤑: {is_premium}"
                        ),
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[[InlineKeyboardButton(text="Profile", url=f"tg://user?id={telegram_id}")]]
                        ),
                    )
                except:
                    pass
