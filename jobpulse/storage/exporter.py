import json
from pathlib import Path


def export_jobs(jobs, output_file):
    job_dicts = [job.to_dict() for job in jobs]
    output_path = Path(output_file)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parents[2] / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(job_dicts, f, indent=2)
