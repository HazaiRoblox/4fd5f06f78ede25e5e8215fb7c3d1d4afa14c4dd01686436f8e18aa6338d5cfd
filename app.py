from flask import Flask, render_template, request
from ddgs import DDGS
from pinscrape import Pinterest
import concurrent.futures
import random
import os

app = Flask(__name__)

def fetch_ddg_images(query, limit=80):
    """Fetch image URLs from DuckDuckGo."""
    urls = []
    try:
        with DDGS() as ddgs:
            # We request slightly more results (80) than needed to enable high randomization
            results = ddgs.images(query, max_results=limit)
            urls = [res.get('image') for res in results if res.get('image')]
    except Exception as e:
        print(f"DuckDuckGo Error: {e}")
    return urls

def fetch_pinterest_images(query, limit=70):
    """Fetch image URLs from Pinterest using pinscrape."""
    urls = []
    try:
        p = Pinterest(sleep_time=1)
        # Fetching up to 70 allows a healthy pool of random images
        urls = p.search(query, limit)
    except Exception as e:
        print(f"Pinterest Error: {e}")
    return urls

@app.route('/', methods=['GET', 'POST'])
def index():
    images = []
    query = ''
    method = 'mix'  # 'mix' is the default option
    
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        method = request.form.get('method', 'mix').strip()
        
        if query:
            if method == 'ddgs':
                # Fetch 80, shuffle them randomly, then slice the top 50
                raw_urls = fetch_ddg_images(query, limit=80)
                random.shuffle(raw_urls)
                images = raw_urls[:50]
                
            elif method == 'pinterest':
                # Fetch 70, shuffle them randomly, then slice the top 50
                raw_urls = fetch_pinterest_images(query, limit=70)
                random.shuffle(raw_urls)
                images = raw_urls[:50]
                
            else:  # mix
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Fetch 50 from each engine concurrently
                    future_ddg = executor.submit(fetch_ddg_images, query, 50)
                    future_pin = executor.submit(fetch_pinterest_images, query, 50)
                    
                    ddg_urls = future_ddg.result()
                    pin_urls = future_pin.result()
                    
                    # Combine results and remove duplicates
                    combined_pool = list(set(ddg_urls + pin_urls))
                    combined_pool = [x for x in combined_pool if x]
                    
                    # Shuffle the combined pool to create a completely random feed
                    random.shuffle(combined_pool)
                    
                    # Slice the final mixed pool down to exactly 50
                    images = combined_pool[:50]

    return render_template('index.html', images=images, query=query, method=method)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
