import logging
import random
import os  # Добавляем импорт os для работы с переменными окружения
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

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

# Варианты ответов
RESPONSES = ["Да", "Нет"]

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Игнорируем команды и нетекстовые сообщения
    if update.message.text and not update.message.text.startswith('/'):
        response = random.choice(RESPONSES)
        try:
            await update.message.reply_text(response)
            username = update.message.from_user.username or "неизвестно"
            logger.info(f"Ответил '{response}' пользователю {username}")
        except Exception as e:
            logger.error(f"Ошибка при отправке ответа: {e}")

# Основная функция
def main():
    app = Application.builder().token(TOKEN).build()

    # Добавляем обработчик для всех текстовых сообщений (кроме команд)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
