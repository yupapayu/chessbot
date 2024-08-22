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
    analysis_result, gif_paths, board = analyzer.analyze(side=side)

    if not analysis_result["mistakes"]:
        await update.message.reply_text("No significant mistakes found in this game.")
        return

    moves = [mistake["move"] for mistake in analysis_result["mistakes"]]
    keyboard = [[InlineKeyboardButton(str(move), callback_data=str(move))] for move in moves]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data['analysis_result'] = analysis_result
    context.user_data['board'] = board

    await update.message.reply_text("Choose a move to analyze:", reply_markup=reply_markup)

async def handle_move_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_move = query.data
    analysis_result = context.user_data.get('analysis_result')
    board = context.user_data.get('board')

    if analysis_result is None:
        await query.edit_message_text(text="Analysis not found. Please try again.")
        return

    # Znalezienie analizy dla wybranego ruchu
    for mistake in analysis_result["mistakes"]:
        # Porównanie ruchu w formacie str, ponieważ selected_move to str
        if str(mistake["move"]) == selected_move:
            full_move_notation = board.san(mistake["move"])
            ai_assistant = AIAssistant()
            ai_description = ai_assistant.generate_analysis([{
                "move": full_move_notation,
                "current_score": mistake["current_score"],
                "previous_score": mistake["previous_score"],
                "best_moves": mistake["best_moves"]}
            ])
            report_generator = ReportGenerator({"mistakes": [mistake]}, ai_description)
            report = report_generator.generate()

            await query.edit_message_text(text=report)
            return

    await query.edit_message_text(text="Selected move not found in the analysis.")
