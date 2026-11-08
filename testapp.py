import os
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enables Cross-Origin requests from the HTML frontend

client = genai.Client()

URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def clean_url(value):
    """Return the value only if it looks like a real http(s) URL, else ''."""
    value = str(value or '').strip()
    return value if URL_RE.match(value) else ''


HEADERS = {
    # Wikimedia asks for a descriptive User-Agent; a browser-like one is safest.
    'User-Agent': 'Mozilla/5.0 (compatible; JourneyMatch/1.0; student project)',
    'Accept': '*/*',
}

# Python's own SSL store is often empty/outdated (e.g. python.org installs on
# macOS), which makes every urllib HTTPS call fail. Reuse certifi's bundle, which
# the Gemini client already depends on, so our lookups work wherever Gemini does.
try:
    import certifi
    import ssl
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = None


def open_url(url, extra_headers=None, timeout=6):
    req = urllib.request.Request(url, headers=dict(HEADERS, **(extra_headers or {})))
    return urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX)


def fetch_json(url):
    with open_url(url) as resp:
        return json.loads(resp.read().decode('utf-8'))


def image_loads(url):
    """
    True  -> the URL really serves an image.
    False -> the server answered, and it is NOT an image (404, HTML page, ...).
    None  -> we could not check (no network, SSL problem, hot-link protection).
             Caller keeps the URL and lets the browser try it.
    """
    if not url:
        return False
    try:
        with open_url(url, {'Range': 'bytes=0-0'}) as resp:
            return resp.getheader('Content-Type', '').lower().startswith('image/')
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429):           # blocked for bots; browser may still load it
            print(f"Image check inconclusive ({e.code}) for {url}")
            return None
        print(f"Image check: {e.code} for {url}")
        return False
    except Exception as e:                     # network / SSL / timeout
        print(f"Image check could not run ({e.__class__.__name__}: {e}) for {url}")
        return None


def wikipedia_search_title(query):
    """Find the best Wikipedia article title for a free-text query."""
    try:
        url = ("https://en.wikipedia.org/w/api.php?action=query&list=search&format=json"
               "&srlimit=1&srsearch=" + urllib.parse.quote(query))
        hits = fetch_json(url).get('query', {}).get('search', [])
        return hits[0]['title'] if hits else ''
    except Exception as e:
        print(f"Wikipedia search failed for '{query}': {e}")
        return ''


def wikipedia_lookup(name, country):
    """
    Image + link from Wikipedia's public REST API (no key needed).
    Returns (image_url, page_url); either may be ''.
    """
    candidates = [f"{name}, {country}" if country else name, name]
    found = wikipedia_search_title(f"{name} {country}".strip())
    if found:
        candidates.insert(0, found)

    for title in candidates:
        try:
            url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
                   + urllib.parse.quote(title.replace(' ', '_')))
            info = fetch_json(url)
            if info.get('type') == 'disambiguation':
                continue
            # Use the thumbnail URL exactly as given: Wikipedia's thumbnail server
            # rejects hand-edited sizes (HTTP 400). Fall back to the original image.
            image = ((info.get('thumbnail') or {}).get('source', '')
                     or (info.get('originalimage') or {}).get('source', ''))
            page = (info.get('content_urls') or {}).get('desktop', {}).get('page', '')
            if image or page:
                return image, page
        except Exception as e:  # network error, 404, bad JSON ...
            print(f"Wikipedia lookup failed for '{title}': {e}")
    return '', ''


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
                'image_url': clean_url(item.get('image_url')),   # picture of the place
                'link': clean_url(item.get('link')),             # page to read more
            })
    return destinations


def fill_missing_media(destinations):
    """
    Make sure every destination has a photo that actually loads, plus a link.
    The model's own image URL is kept only if it really serves an image;
    otherwise Wikipedia's photo for the place is used.
    """
    for d in destinations:
        if image_loads(d['image_url']) is False:   # definitely broken -> drop it
            d['image_url'] = ''
        if d['image_url'] and d['link']:
            continue
        image, page = wikipedia_lookup(d['name'], d['country'])
        if not d['image_url'] and image and image_loads(image) is not False:
            d['image_url'] = image
        d['link'] = d['link'] or page
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
            "why": "One sentence tying it back to the user's three words.",
            "image_url": "A direct https link to a real, freely usable photo of the place (prefer upload.wikimedia.org). Use an empty string if unsure.",
            "link": "An https link where the user can read more, e.g. the official tourism site or the Wikipedia page."
          }}
        ]
        Only include URLs you are confident exist; never invent them.
        """

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        destinations = fill_missing_media(parse_destinations(response.text))

        # Print the response to the terminal console
        print("\n=== GEMINI API RESPONSE ===")
        print(response.text)
        print(f"--- parsed {len(destinations)} destination(s) ---")
        for d in destinations:
            print(f"  {d['name']}: image={d['image_url'] or '-'} link={d['link'] or '-'}")
        print("===========================\n")

        return jsonify({
            'success': True,
            'destinations': destinations,      # structured -> carousel slides (with images + links)
            'recommendation': response.text    # raw text fallback
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
