from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from config import URL
from jobpulse.ingestion.models import Job
def parse_html(html):
    soup=BeautifulSoup(html,"lxml")
    return soup

def extract_jobs(soup):
    job_list=soup.find("ol",class_="list-recent-jobs")
    cards=job_list.find_all("li")
        

    jobs=[]

    for i,card in enumerate(cards):
        company=card.find("span",class_="listing-company-name")
        title_name=company.find("a")
        br=company.find("br")
        company_name=br.next_sibling.strip()
        location=card.find("span",class_="listing-location")
        posted_date=card.find("span",class_="listing-posted").get_text(strip=True)
        posted_date=posted_date.replace("Posted:","")
        posted_date=datetime.strptime(posted_date,"%d %B %Y" ).date()
        job_url = urljoin(URL, title_name['href'])
        jobs.append(Job(title_name.get_text(),company_name,location.get_text(),posted_date,job_url))

    return jobs