# import requests

# URL = "https://weworkremotely.com/categories/remote-programming-jobs"




# def fetch_html():
    # response=requests.get(URL)
    # print(response.url)
    # response.raise_for_status()
    
    # return response.text
import requests

URL = "https://remoteok.com/remote-dev-jobs"

def fetch_html():
    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}
    response = requests.get(URL,headers=headers)

    print("Status:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("URL:", response.url)

    response.raise_for_status()
    return response.text
    

    # TODO:
    # 1. Send GET request
    # 2. Check for request errors
    # 3. Return response.text