from ingestion.fetch import fetch_html
from ingestion.parser import parse_html


def main():

    html = fetch_html()

    soup=parse_html(html)
    table=soup.find("table",id="jobsboard")
    rows=table.find_all("tr")
    print(len(rows))
    row = rows[3]
    
    print(row.prettify()[:2500])
    for i,row in enumerate(rows):
        print(i,row.attrs)
    
    print(html.lower().count("python"))
    print(html.lower().count("engineer"))
        



if __name__ == "__main__":
    main()