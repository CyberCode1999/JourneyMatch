import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enables Cross-Origin requests from the HTML frontend

client = genai.Client()

@app.route('/api/recommend', methods=['POST'])
def get_recommendation():
    try:
        data = request.get_json()
        
        # Get the 'question' field (3 words) sent from HTML
        three_words = data.get('question', '')

        if not three_words:
            return jsonify({'error': 'No input provided'}), 400

        prompt = f"""
        You are an expert travel assistant. Based on these 3 words describing what the user is looking for: "{three_words}",
        recommend 3 ideal destinations or places. Keep the recommendations concise, engaging, and relevant to the 3 words provided.
        """

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        # Print the response to the terminal console
        print("\n=== GEMINI API RESPONSE ===")
        print(response.text)
        print("===========================\n")

        return jsonify({
            'success': True,
            'recommendation': response.text
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)