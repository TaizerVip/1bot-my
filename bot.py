import logging
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

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
DEFAULT_CHANCE = 5  # 5 % шанс по умолчанию (от 0 до 100)
chance = DEFAULT_CHANCE

# Список подарков
GIFTS = [
    "🎁 Подарочный сертификат",
    "🎈 Воздушный шарик",
    "🏆 Трофей недели",
    "💎 Кристалл удачи",
    "☕ Чашка кофе"
]

# Клавиатура админ‑меню
def get_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ +10 %", callback_data="chance_up_10"),
            InlineKeyboardButton("➖ -10 %", callback_data="chance_down_10")
        ],
        [InlineKeyboardButton("🔄 Сброс к 5 %", callback_data="reset_chance")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчик команды /admin
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет прав администратора!")
        return

    await update.message.reply_text(
        f"Текущий шанс выпадения подарка: {chance}%",
        reply_markup=get_admin_keyboard()
    )

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
    if data == "chance_up_10":
        chance = min(chance + 10, 100)
        await query.edit_message_text(
            f"✅ Шанс увеличен до {chance}%",
            reply_markup=get_admin_keyboard()
        )
    elif data == "chance_down_10":
        chance = max(chance - 10, 0)
        await query.edit_message_text(
            f"✅ Шанс уменьшен до {chance}%",
            reply_markup=get_admin_keyboard()
        )
    elif data == "reset_chance":
        chance = DEFAULT_CHANCE
        await query.edit_message_text(
            f"✅ Шанс сброшен до {DEFAULT_CHANCE}%",
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
            if random.randint(1, 100) <= chance:
                gift = random.choice(GIFTS)
                await update.message.reply_text(f"🎉 Вам выпал подарок! {gift} 🎉")
                logger.info(f"Подарок выдан в чате {update.message.chat.id}")

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
