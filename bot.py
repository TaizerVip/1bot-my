import logging
import random
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ВАШ ТОКЕН БОТА (ЗАМЕНИТЕ НА СВОЙ!)
TOKEN = "8769116926:AAF9CrgwABECHO2bUDN9lzUR7n6RIf14ZkI"  # ← ВСТАВЬТЕ ТОКЕН СЮДА!

# Варианты ответов
RESPONSES = ["Да", "Нет"]

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Игнорируем команды и нетекстовые сообщения
    if update.message.text and not update.message.text.startswith('/'):
        response = random.choice(RESPONSES)
        try:
            await update.message.reply_text(response)
            logger.info(f"Ответил '{response}' пользователю {update.message.from_user.username}")
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
