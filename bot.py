import logging
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, filters, ContextTypes,
    CommandHandler, CallbackQueryHandler
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в переменных окружения")

# ID администраторов (замените на реальные ID)
ADMIN_IDS = [8135803663]  # Замените на ID администраторов

# Настройки по умолчанию
DEFAULT_CHANCE = 0.05  # 5 % шанс по умолчанию
chance = DEFAULT_CHANCE

# Хранилище для статистики (в продакшене используйте БД)
user_gifts = {}  # user_id: count

# Клавиатура админ‑меню
def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [
            InlineKeyboardButton("➕ +1 %", callback_data="chance_up_1"),
            InlineKeyboardButton("➖ -1 %", callback_data="chance_down_1")
        ],
        [
            InlineKeyboardButton("➕ +5 %", callback_data="chance_up_5"),
            InlineKeyboardButton("➖ -5 %", callback_data="chance_down_5")
        ],
        [InlineKeyboardButton("🔄 Сброс к 5 %", callback_data="reset_chance")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчик команд для админов
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет прав администратора!")
        return
    
    stats_text = "📊 Статистика бота:\n"
    total_gifts = sum(user_gifts.values())
    stats_text += f"Всего подарков выдано: {total_gifts}\n"
    stats_text += f"Текущий шанс: {chance * 100:.1f} %"
    
    await update.message.reply_text(stats_text, reply_markup=get_admin_keyboard())

# Обработчик нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
        await query.edit_message_text("❌ У вас нет прав для этого действия!")
        return
    
    global chance
    
    data = query.data
    if data == "stats":
        stats_text = "📊 Подробная статистика:\n\n"
        for user_id, count in user_gifts.items():
            stats_text += f"Пользователь {user_id}: {count} подарков\n"
        await query.edit_message_text(stats_text)
    
    elif data == "chance_up_1":
        chance = min(chance + 0.01, 1.0)
        await query.edit_message_text(
            f"✅ Шанс увеличен до {chance * 100:.1f} %",
            reply_markup=get_admin_keyboard()
        )
    elif data == "chance_down_1":
        chance = max(chance - 0.01, 0.0)
        await query.edit_message_text(
            f"✅ Шанс уменьшен до {chance * 100:.1f} %",
            reply_markup=get_admin_keyboard()
        )
    elif data == "chance_up_5":
        chance = min(chance + 0.05, 1.0)
        await query.edit_message_text(
            f"✅ Шанс увеличен до {chance * 100:.1f} %",
            reply_markup=get_admin_keyboard()
        )
    elif data == "chance_down_5":
        chance = max(chance - 0.05, 0.0)
        await query.edit_message_text(
            f"✅ Шанс уменьшен до {chance * 100:.1f} %",
            reply_markup=get_admin_keyboard()
        )
    elif data == "reset_chance":
        chance = DEFAULT_CHANCE
        await query.edit_message_text(
            f"✅ Шанс сброшен до {DEFAULT_CHANCE * 100:.1f} %",
            reply_markup=get_admin_keyboard()
        )

# Обработчик текстовых сообщений (выдача подарков)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Игнорируем команды и нетекстовые сообщения
    if update.message.text and not update.message.text.startswith('/'):
        # Проверяем, что сообщение из чата (не личное)
        chat_type = update.message.chat.type
        if chat_type in ['group', 'supergroup']:
            # Рандомная выдача подарка
            if random.random() < chance:
                user_id = update.message.from_user.id
                username = update.message.from_user.username or "Пользователь"
                
                # Увеличиваем счётчик подарков для пользователя
                if user_id in user_gifts:
                    user_gifts[user_id] += 1
                else:
                    user_gifts[user_id] = 1
                
                gift_text = f"🎁 {username}, вам выпал подарок! 🎉"
                await update.message.reply_text(gift_text)
                logger.info(f"Подарок выдан пользователю {username} (ID: {user_id})")

# Основная функция
def main():
    app = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

    # Добавляем обработчик для всех текстовых сообщений (кроме команд)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
