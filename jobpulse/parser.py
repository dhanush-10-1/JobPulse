from bs4 import BeautifulSoup
def parse_html(html):
    soup=BeautifulSoup(html,"lxml")
    return soup