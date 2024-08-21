import chess.pgn
import chess.engine
import chess.svg
from config import STOCKFISH_PATH
from PIL import Image, ImageDraw, ImageFont
import io
import cairosvg


class GameAnalyzer:
    def __init__(self, pgn_file):
        self.pgn_file = pgn_file

    def analyze(self, side=None):
        with open(self.pgn_file, "r") as pgn:
            game = chess.pgn.read_game(pgn)

        board = game.board()
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        analysis_result = {
            "mistakes": []
        }

        previous_score = None
        gif_paths = []

        for idx, move in enumerate(game.mainline_moves()):
            # Pominięcie ruchów przeciwnika
            if (side == 'white' and idx % 2 != 0) or (side == 'black' and idx % 2 == 0):
                board.push(move)
                continue

            board.push(move)
            infos = engine.analyse(board, chess.engine.Limit(time=0.5), multipv=3)
            best_info = infos[0]
            score = best_info['score'].relative

            if isinstance(score, chess.engine.Cp):
                score = score.score()

            if previous_score is not None and abs(score - previous_score) > 320:
                best_moves = [info["pv"][0] for info in infos[:3]]
                analysis_result["mistakes"].append({
                    "move": move,
                    "current_score": score,
                    "previous_score": previous_score,
                    "best_moves": best_moves
                })

                frames = []
                for best_move in best_moves:
                    board.push(best_move)
                    svg = chess.svg.board(board=board)
                    png_image = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
                    img = Image.open(io.BytesIO(png_image))

                    draw = ImageDraw.Draw(img)
                    font = ImageFont.load_default()
                    explanation = f"Suggested move: {best_move}\n"
                    explanation += f"Evaluation: {score} (better than previous)\n"
                    draw.text((10, 10), explanation, font=font, fill=(255, 255, 255))

                    frames.append(img)
                    board.pop()

                gif_path = f"best_move_{idx}.gif"
                frames[0].save(gif_path, save_all=True, append_images=frames[1:], loop=0, duration=1000)
                gif_paths.append(gif_path)

            previous_score = score

        engine.quit()
        return analysis_result, gif_paths


