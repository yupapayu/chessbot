class ReportGenerator:
    def __init__(self, analysis_result):
        self.analysis_result = analysis_result

    def generate(self):
        report = "Game Analysis Report (like a coach):\n"

        if not self.analysis_result["mistakes"]:
            report += "Congratulations! No significant mistakes found in this game.\n"
        else:
            for mistake in self.analysis_result["mistakes"]:
                move = mistake["move"]
                score_change = mistake["current_score"] - mistake["previous_score"]

                report += f"\nYou made a mistake with the move {move}. You lost {abs(score_change)} points in evaluation.\n"
                report += "Here are some better alternatives you could have considered:\n"

                for idx, best_move in enumerate(mistake["best_moves"], 1):
                    report += f"{idx}. {best_move}\n"

        return report
