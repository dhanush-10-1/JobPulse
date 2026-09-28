from datetime import datetime
from urllib.parse import urljoin
import re
from bs4 import BeautifulSoup
from config import URL
from jobpulse.ingestion.models import Job


def _text(soup, selectors):
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            value = element.get_text(" ", strip=True)
            if value:
                return value
    return None


def extract_job_details(soup):
    return {
        "description": _text(
            soup,
            [".job-description", "#job-description", '[itemprop="description"]'],
        ),
        "employment_type": _text(
            soup,
            ['[itemprop="employmentType"]', ".employment-type", ".listing-job-type"],
        ),
        "salary": _text(
            soup,
            ['[itemprop="baseSalary"]', ".salary", ".listing-salary"],
        ),
    }
def parse_html(html):
    soup=BeautifulSoup(html,"lxml")
    return soup

def extract_jobs(soup, detail_fetcher=None):
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
        posted_date=posted_date.replace("Posted:","").strip()
        posted_date=datetime.strptime(posted_date,"%d %B %Y" ).date()
        job_url = urljoin(URL, title_name['href'])
        details = extract_job_details(card)
        if detail_fetcher and not details["description"]:
            try:
                fetched_details = extract_job_details(parse_html(detail_fetcher(job_url)))
                details.update(
                    {
                        key: value
                        for key, value in fetched_details.items()
                        if value is not None
                    }
                )
            except Exception:
                pass
        source_id = re.search(r"/jobs/(\d+)/", job_url)
        jobs.append(
            Job(
                title_name.get_text(),
                company_name,
                location.get_text(),
                posted_date,
                job_url,
                source_job_id=source_id.group(1) if source_id else None,
                description=details["description"],
                employment_type=details["employment_type"],
                salary=details["salary"],
            )
        )

    return jobs