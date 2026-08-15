import requests
from jobpulse.utils.logger import logger

def fetch_html(url):
    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}
    try:
        response = requests.get(url,headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.exception("failed to fetch html %s",url)
        raise 
    
    return response.text
    

    # TODO:
    # 1. Send GET request
    # 2. Check for request errors
    # 3. Return response.text