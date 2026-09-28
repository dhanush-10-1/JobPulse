class Job():
    def __init__(self,title,company,location,posted_date,url,source="python.org",first_seen_at=None,last_seen_at=None,is_active=True,source_job_id=None,description=None,employment_type=None,salary=None):
        self.title=title
        self.company=company
        self.location=location
        self.posted_date=posted_date
        self.url=url
        self.source=source
        self.first_seen_at=first_seen_at
        self.last_seen_at=last_seen_at
        self.is_active=is_active
        self.source_job_id=source_job_id
        self.description=description
        self.employment_type=employment_type
        self.salary=salary
    def to_dict(self):
        return{
            "title":self.title,
            "company":self.company,
            "location":self.location,
            "posted_date":self.posted_date.isoformat(),
            "url":self.url,
            "source":self.source,
            "source_job_id":self.source_job_id,
            "description":self.description,
            "employment_type":self.employment_type,
            "salary":self.salary
        }
    @classmethod
    def from_row(cls,row):
        return cls(*row)