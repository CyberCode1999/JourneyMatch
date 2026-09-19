# JourneyMatch

JourneyMatch is a travel recommendation web app that helps users discover destination ideas based on a short prompt or preference. The app uses a simple quiz flow and a Gemini-powered backend to recommend destinations.

## Overview

- Users start from the landing page and click "Start the Journey"
- They answer a short travel question
- The app recommends three destination options
- Results are displayed in a carousel-style UI

## Features

- Minimal travel quiz flow
- AI-generated destination recommendations
- Responsive front-end layout
- Flask backend with CORS enabled
- Gemini integration for recommendation logic

## Project structure

- `index.html` — landing page
- `question.html` — question form page
- `result.html` — results display page
- `Main.js` — client-side logic
- `style.css` — application styling
- `testapp.py` — Flask API server and Gemini integration
- `Images/` — destination images
- `AIproject/` — Python virtual environment

## Getting started

### 1. Open the project

```bash
cd /path/to/JourneyMatch
```

### 2. Activate the virtual environment

If using WSL or Linux:

```bash
source AIproject/bin/activate
```

If using Windows PowerShell:

```powershell
.\AIproject\Scripts\Activate.ps1
```

### 3. Add your API key

Create a `.env` file in the project root with your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the app

```bash
python testapp.py
```

Then open:

```text
http://localhost:5000
```

## How it works

The Flask app exposes a `/api/recommend` endpoint. It receives a short travel prompt and sends it to the Gemini model, which returns structured destination suggestions in JSON format. The front-end then renders those results.

## Planned improvements

- Add more questions to the questionnaire
- Give each question a unique ID and label on the same page
- Expand the about page with more context
- Improve the design using a more detailed Figma mockup

## Notes

The project currently uses a Figma design as a reference for future UI improvements:

- https://www.figma.com/design/14xBhl1vTW7LG3CHW3X2v5/My-Trip?node-id=0-1&p=f&t=kpz0u97c0ErQZQzA-0

## License

This project is currently for personal or academic use and has no formal license file yet.