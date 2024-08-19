# bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes
from analysis.analyzer import GameAnalyzer
from analysis.report import ReportGenerator

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Chess Analyzer Bot! Send me a PGN file to get started.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a PGN file of your game, and I'll analyze it for you.")

async def handle_pgn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = f"pgn_files/{file.file_id}.pgn"
    await file.download_to_drive(file_path)

    analyzer = GameAnalyzer(file_path)
    analysis_result, gif_path = analyzer.analyze()

    report_generator = ReportGenerator(analysis_result)
    report = report_generator.generate()

    max_message_length = 4096
    for i in range(0, len(report), max_message_length):
        await update.message.reply_text(report[i:i + max_message_length])

    await update.message.reply_animation(animation=open(gif_path, 'rb'))
