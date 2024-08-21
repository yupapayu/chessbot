from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot.handlers import start, help_command, handle_pgn, handle_choice, handle_move_choice

class TelegramBot:
    def __init__(self, token):
        self.application = ApplicationBuilder().token(token).build()

        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(MessageHandler(filters.Document.ALL & filters.Document.FileExtension("pgn"), handle_pgn))
        self.application.add_handler(CallbackQueryHandler(handle_choice, pattern='^white|black$'))
        self.application.add_handler(CallbackQueryHandler(handle_move_choice))

    def run(self):
        self.application.run_polling()


