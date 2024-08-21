from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from analysis.analyzer import GameAnalyzer
from analysis.report import ReportGenerator
from analysis.ai_assistant import AIAssistant
from config import OPENAI_API_TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Analyze White", callback_data='white')],
        [InlineKeyboardButton("Analyze Black", callback_data='black')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose which side to analyze:", reply_markup=reply_markup)

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data['side_to_analyze'] = query.data

    await query.edit_message_text(text=f"Selected side: {query.data}. Now send the PGN file.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a PGN file of your game, and I'll analyze it for you.")


async def handle_pgn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = f"pgn_files/{file.file_id}.pgn"
    await file.download_to_drive(file_path)

    analyzer = GameAnalyzer(file_path)
    side = context.user_data.get('side_to_analyze')
    analysis_result, gif_paths = analyzer.analyze(side=side)

    moves = [mistake["move"] for mistake in analysis_result["mistakes"]]
    keyboard = [[InlineKeyboardButton(str(move), callback_data=str(move))] for move in moves]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data['analysis_result'] = analysis_result

    await update.message.reply_text("Choose a move to analyze:", reply_markup=reply_markup)

async def handle_move_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_move = query.data
    analysis_result = context.user_data['analysis_result']

    # Find the specific move analysis
    for mistake in analysis_result["mistakes"]:
        if mistake["move"] == selected_move:
            ai_assistant = AIAssistant(api_key=OPENAI_API_TOKEN)
            ai_description = ai_assistant.generate_analysis([mistake])
            report_generator = ReportGenerator({"mistakes": [mistake]}, ai_description)
            report = report_generator.generate()

            await query.edit_message_text(text=report)
            break