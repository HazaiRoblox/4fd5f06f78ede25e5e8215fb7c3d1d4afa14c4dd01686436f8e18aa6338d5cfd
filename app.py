from flask import Flask, render_template, request, jsonify
from ddgs import DDGS
from pinscrape import Pinterest
import concurrent.futures
import random

app = Flask(__name__)

def fetch_ddg_images(query, limit):
    """Fetch image URLs from DuckDuckGo."""
    urls = []
    try:
        with DDGS() as ddgs:
            results = ddgs.images(query, max_results=limit)
            urls = [res.get('image') for res in results if res.get('image')]
    except Exception as e:
        print(f"DuckDuckGo Error: {e}")
    return urls

def fetch_pinterest_images(query, limit):
    """Fetch image URLs from Pinterest using pinscrape."""
    urls = []
    try:
        p = Pinterest(sleep_time=1)
        urls = p.search(query, limit)
    except Exception as e:
        print(f"Pinterest Error: {e}")
    return urls

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def api_search():
    query = request.args.get('query', '').strip()
    method = request.args.get('method', 'mix').strip()
    page = int(request.args.get('page', 1))
    
    limit = 50
    offset = (page - 1) * limit
    
    # Calculate target range to pull from the APIs
    total_to_fetch = min(offset + limit, 1000)
    
    images = []
    if query:
        if method == 'ddgs':
            raw_urls = fetch_ddg_images(query, limit=total_to_fetch)
            page_slice = raw_urls[offset : offset + limit]
            random.shuffle(page_slice)
            images = page_slice
            
        elif method == 'pinterest':
            # Cap Pinterest scraping to keep response times fast
            pin_fetch_limit = min(total_to_fetch, 250)
            raw_urls = fetch_pinterest_images(query, limit=pin_fetch_limit)
            page_slice = raw_urls[offset : offset + limit]
            random.shuffle(page_slice)
            images = page_slice
            
        else:  # mix
            half_total = total_to_fetch // 2
            half_offset = offset // 2
            half_limit = limit // 2
            
            # Ensure index safety limits
            if half_total < 1:
                half_total = 1
                
            pin_fetch_limit = min(half_total, 125)
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_ddg = executor.submit(fetch_ddg_images, query, half_total)
                future_pin = executor.submit(fetch_pinterest_images, query, pin_fetch_limit)
                
                ddg_res = future_ddg.result()
                pin_res = future_pin.result()
                
                ddg_slice = ddg_res[half_offset : half_offset + half_limit]
                pin_slice = pin_res[half_offset : half_offset + half_limit]
                
                # Combine, deduplicate, and shuffle
                combined = list(set(ddg_slice + pin_slice))
                combined = [x for x in combined if x]
                random.shuffle(combined)
                images = combined[:limit]

    return jsonify({"images": images})

if __name__ == '__main__':
    app.run(debug=True)
