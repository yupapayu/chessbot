import openai
from openai import OpenAI
from config import OPENAI_API_TOKEN


class AIAssistant:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_TOKEN)

    def generate_analysis(self, analysis_result):
        descriptions = []
        for mistake in analysis_result["mistakes"]:
            prompt = f"Explain why the move {mistake['move']} was a mistake and suggest better alternatives."

            stream = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a chess coach."},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )

            description = ""
            for chunk in stream:
                if chunk.choices[0].delta.get("content"):
                    description += chunk.choices[0].delta["content"]

            descriptions.append(description.strip())

        return descriptions
