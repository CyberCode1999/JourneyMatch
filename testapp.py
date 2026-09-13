import os
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enables Cross-Origin requests from the HTML frontend

client = genai.Client()


def parse_destinations(text):
    """Pull a list of destination dicts out of the model's reply."""
    cleaned = text.strip()

    # Strip ```json ... ``` fences if the model added them
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1)

    # Fall back to the first [...] block found anywhere in the reply
    if not cleaned.startswith('['):
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    destinations = []
    for item in data:
        if isinstance(item, dict) and item.get('name'):
            destinations.append({
                'name': str(item.get('name', '')),
                'country': str(item.get('country', '')),
                'description': str(item.get('description', '')),
                'why': str(item.get('why', '')),
            })
    return destinations


@app.route('/api/recommend', methods=['POST'])
def get_recommendation():
    try:
        data = request.get_json()

        # Get the 'question' field (3 words) sent from HTML
        three_words = data.get('question', '')

        if not three_words:
            return jsonify({'error': 'No input provided'}), 400

        prompt = f"""
        You are an expert travel assistant. Based on these 3 words describing what the user is
        looking for: "{three_words}", recommend exactly 3 ideal destinations.

        Reply with ONLY a JSON array, no markdown fences and no commentary, in this shape:
        [
          {{
            "name": "City or place name",
            "country": "Country",
            "description": "Two or three engaging sentences about the destination.",
            "why": "One sentence tying it back to the user's three words."
          }}
        ]
        """

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        destinations = parse_destinations(response.text)

        # Print the response to the terminal console
        print("\n=== GEMINI API RESPONSE ===")
        print(response.text)
        print(f"--- parsed {len(destinations)} destination(s) ---")
        print("===========================\n")

        return jsonify({
            'success': True,
            'destinations': destinations,      # structured -> carousel slides
            'recommendation': response.text    # raw text fallback
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
