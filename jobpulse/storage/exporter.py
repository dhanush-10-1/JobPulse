import json
def export_jobs(jobs,output_file):
    job_dicts=[job.to_dict() for job in jobs]
    with open(output_file,"w",encoding="utf-8") as f:
        json.dump(job_dicts,f,indent=2)
