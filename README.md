# JourneyMatch

JourneyMatch is a travel recommendation web app that turns a short travel prompt into AI-generated destination ideas. Users enter a few words describing the kind of trip they want, and the app suggests a few destinations with short explanations and reasons based on those preferences.

The project combines a lightweight Flask backend with a browser-based front end and uses Google's GenAI model to generate travel suggestions.

## Features

- Simple travel prompt flow from landing page to recommendation results
- AI-powered destination matching using Gemini
- Results rendered as a destination carousel with title, country, description, and recommendation reason
- Front-end pages for the landing screen, question screen, and results screen
- Flask API with CORS enabled for browser access
- Support for fallback handling when no destination matches are found

## Tech stack

- Python 3
- Flask
- Flask-CORS
- Google GenAI SDK
- HTML, CSS, and JavaScript
- dotenv for environment management

## Project structure

- `index.html` — landing page with branding and travel inspiration
- `question.html` — question form where users enter a travel prompt
- `result.html` — displays the generated destination recommendations
- `travelplan.html` — travel planning page for follow-up trip planning
- `noresult.html` — empty-state page when no recommendations are returned
- `Main.js` — front-end logic and interactions
- `style.css` — app styling and layout
- `testapp.py` — Flask server and Gemini integration
- `Images/` — onboarding and destination imagery
- `AIproject/` — local Python virtual environment
- `.env` — local environment file containing your API key (not committed)

## How it works

1. The user starts on the landing page and selects the option to begin.
2. They enter a short phrase describing their ideal trip, such as "beach relaxing budget" or "adventure mountain food".
3. The browser sends the prompt to the Flask backend.
4. The backend calls the Gemini model with a structured prompt asking for exactly three destination recommendations.
5. The response is parsed and returned as JSON.
6. The front end displays the results in a results page with destination details and recommendation reasons.

## Local setup

### 1. Open the project directory

```bash
cd /path/to/JourneyMatch
```

### 2. Activate the virtual environment

On WSL or Linux:

```bash
source AIproject/bin/activate
```

On Windows PowerShell:

```powershell
.\AIproject\Scripts\Activate.ps1
```

### 3. Add your API key

Create a `.env` file in the project root with your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

> If you are using a Google AI project, make sure your API key is valid and has access to the relevant model.

### 4. Run the app

```bash
python testapp.py
```

Then open the app in your browser:

```text
http://localhost:5000
```

## API behavior

The Flask app exposes a `POST /api/recommend` endpoint.

Request body:

```json
{
  "question": "beach relaxing budget"
}
```

Expected response:

```json
{
  "success": true,
  "destinations": [
    {
      "name": "Bali",
      "country": "Indonesia",
      "description": "A tropical destination with beaches, temples, and a relaxed pace.",
      "why": "This matches your interest in a relaxed, beach-focused getaway."
    }
  ],
  "recommendation": "raw model output"
}
```

The backend parses the model response to extract a JSON array and returns structured destination objects for the front end.

## Notes

- The app currently uses a single short prompt field to generate recommendations.
- The backend expects the `question` value to be a short phrase or a few keywords.
- The app is designed for a simple demo or prototype flow rather than a full production travel platform.
- There is no formal license file in the repository yet, so the project is currently treated as personal or academic use unless otherwise stated.

## Roadmap / future improvements

- Add a multi-question questionnaire with unique labels and IDs
- Improve the result display and recommendation formatting
- Expand error handling and validation for invalid prompts
- Add stronger travel filtering and personalization logic
- Refine the UI using the existing Figma design as a visual reference

## Figma reference

The project was initially informed by a visual mockup in Figma:

https://www.figma.com/design/14xBhl1vTW7LG3CHW3X2v5/My-Trip?node-id=0-1&p=f&t=kpz0u97c0ErQZQzA-0

## Troubleshooting

- If the app cannot connect to Gemini, verify that your `.env` file exists and `GEMINI_API_KEY` is set correctly.
- If you receive a CORS error, confirm the Flask backend is running and that the frontend is calling the correct local URL.
- If the result page shows no recommendations, check the model response in the terminal output and validate that the prompt is meaningful enough for the model.
- If the environment is not activated, reinstall dependencies or use the included virtual environment in `AIproject/`.

## License

This project currently has no formal open-source license file in the repository.