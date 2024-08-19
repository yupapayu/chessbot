from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import start, help_command, handle_pgn

class TelegramBot:
    def __init__(self, token):
        self.application = ApplicationBuilder().token(token).build()

        # Registering handlers
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(MessageHandler(filters.Document.ALL & filters.Document.FileExtension("pgn"), handle_pgn))

    def run(self):
        self.application.run_polling()


