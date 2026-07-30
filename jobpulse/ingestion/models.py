class Job():
    def __init__(self,title,company,location,posted_date,url):
        self.title=title
        self.company=company
        self.location=location
        self.posted_date=posted_date
        self.url=url
    def to_dict(self):
        return{
            "title":self.title,
            "company":self.company,
            "location":self.location,
            "posted_date":self.posted_date,
            "url":self.url
        }