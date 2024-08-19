from bot.telegram_bot import TelegramBot
from config import TELEGRAM_API_TOKEN

def main():
    bot = TelegramBot(token=TELEGRAM_API_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
