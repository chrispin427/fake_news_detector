import requests

API_KEY = "YOUR_API_KEY"

def check_news_api(query):
    url = "https://newsapi.org/v2/everything"
    
    params = {
        "q": query,
        "apiKey": API_KEY,
        "language": "en",
        "pageSize": 5
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        return data.get("totalResults", 0)
    
    except Exception as e:
        print("Error:", e)
        return 0