import requests

URL = "https://weworkremotely.com/categories/remote-programming-jobs"
r=requests.get(URL)


def fetch_html():
    r=requests.get(URL)
    r.raise_for_status()
    return r.text
    

    # TODO:
    # 1. Send GET request
    # 2. Check for request errors
    # 3. Return response.text