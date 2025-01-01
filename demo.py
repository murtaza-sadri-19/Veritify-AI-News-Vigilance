import httpx
import pandas as pd

def google_search(api_key, search_engine_id, query, **params):
    base_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        **params
    }
    response = httpx.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

# API credentials
api_key = 'AIzaSyC6oIUD2f1iuXGadfVPksbAQpHJSvcFtvk'
search_engine_id = '5047be7447f514341'
query = 'Virat Kohli retirement from international T20'

# Collect search results
search_results = []
for i in range(1, 100, 10):
    response = google_search(
        api_key=api_key,
        search_engine_id=search_engine_id,
        query=query,
        start=i
    )
    search_results.extend(response.get('items', []))
    if len(search_results) >= 5:  # Stop if we've collected at least 5 results
        break

# Extract top 5 titles
top_titles = [result['title'] for result in search_results[:5]]

# Print top 5 titles
print("Top 5 Headlines:")
for idx, title in enumerate(top_titles, start=1):
    print(f"{idx}: {title}")

# Save to CSV (optional, for further debugging)
