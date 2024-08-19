import chess.pgn
import chess.engine
import chess.svg
from config import STOCKFISH_PATH
from PIL import Image
import imageio
import io
import cairosvg


class GameAnalyzer:
    def __init__(self, pgn_file):
        self.pgn_file = pgn_file

    def analyze(self):
        with open(self.pgn_file, "r") as pgn:
            game = chess.pgn.read_game(pgn)

        board = game.board()
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        analysis_result = {
            "mistakes": []
        }

        move_count = 0
        previous_score = None
        frames = []

        for move in game.mainline_moves():
            board.push(move)
            infos = engine.analyse(board, chess.engine.Limit(time=0.5), multipv=3)
            best_info = infos[0]
            score = best_info['score'].relative

            if isinstance(score, chess.engine.Cp):
                score = score.score()

            if previous_score is not None and abs(score - previous_score) > 100:
                best_moves = [info["pv"][0] for info in infos[:3]]
                analysis_result["mistakes"].append({
                    "move": move,
                    "current_score": score,
                    "previous_score": previous_score,
                    "best_moves": best_moves
                })

                for best_move in best_moves:
                    board.push(best_move)
                    svg = chess.svg.board(board=board)
                    png_image = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
                    img = Image.open(io.BytesIO(png_image))
                    frames.append(img)
                    board.pop()

            previous_score = score
            move_count += 1

        engine.quit()
        gif_path = "best_moves.gif"
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], loop=0, duration=500)
        return analysis_result, gif_path
