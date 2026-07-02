# Image Search (DuckDuckGo + Pinterest)

## Setup

pip install -r requirements.txt

pinscrape uses Selenium to drive Chrome, so you also need:
- Google Chrome installed
- A matching chromedriver on your PATH (https://chromedriver.chromium.org/)

## Run

python app.py

Then open http://localhost:5000

## Usage

Type a search term, pick a source (All / DuckDuckGo / Pinterest), press Search.
Click any image in the results to copy its direct image URL to your clipboard.
