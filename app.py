from flask import Flask, render_template, request
from ddgs import DDGS
from pinscrape import Pinterest
import concurrent.futures
import random

app = Flask(__name__)

def fetch_ddg_images(query, limit=150):
    """Fetch image URLs from DuckDuckGo."""
    urls = []
    try:
        with DDGS() as ddgs:
            # We request a larger pool of 150 to guarantee at least 100 highly randomized items
            results = ddgs.images(query, max_results=limit)
            urls = [res.get('image') for res in results if res.get('image')]
    except Exception as e:
        print(f"DuckDuckGo Error: {e}")
    return urls

def fetch_pinterest_images(query, limit=130):
    """Fetch image URLs from Pinterest using pinscrape."""
    urls = []
    try:
        p = Pinterest(sleep_time=1)
        # Fetching up to 130 allows a healthy pool of random images to slice from
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
                # Fetch 150, shuffle, and slice the top 100
                raw_urls = fetch_ddg_images(query, limit=150)
                random.shuffle(raw_urls)
                images = raw_urls[:100]
                
            elif method == 'pinterest':
                # Fetch 130, shuffle, and slice the top 100
                raw_urls = fetch_pinterest_images(query, limit=130)
                random.shuffle(raw_urls)
                images = raw_urls[:100]
                
            else:  # mix
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Fetch 100 from each engine concurrently
                    future_ddg = executor.submit(fetch_ddg_images, query, 100)
                    future_pin = executor.submit(fetch_pinterest_images, query, 100)
                    
                    ddg_urls = future_ddg.result()
                    pin_urls = future_pin.result()
                    
                    # Combine results and remove duplicates
                    combined_pool = list(set(ddg_urls + pin_urls))
                    combined_pool = [x for x in combined_pool if x]
                    
                    # Shuffle the combined pool to create a completely random feed
                    random.shuffle(combined_pool)
                    
                    # Slice the final mixed pool down to exactly 100
                    images = combined_pool[:100]

    return render_template('index.html', images=images, query=query, method=method)

if __name__ == '__main__':
    app.run(debug=True)
