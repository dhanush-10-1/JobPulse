"""Prompts used by the future job enrichment service."""

JOB_ENRICHMENT_SYSTEM_PROMPT = """
Extract structured information from a job posting. Return only the requested
fields as JSON. Use empty lists for missing list fields and empty strings for
unknown scalar fields. Use null for experience_years when no explicit numeric
experience requirement is stated. Convert explicit experience such as "4+
years" to experience_years: 4.

Normalize seniority to exactly one of: Internship, Entry Level, Junior, Mid
Level, Senior, Staff, Lead, Principal, Manager, Director, Unknown. Do not put
experience text such as "4+ years" in seniority.

employment_type must be exactly one of: Full Time, Part Time, Contract,
Internship, Temporary, Freelance, Unknown. Use Unknown unless the posting
explicitly states an employment arrangement. Never infer it from a department,
role, technology, category, or job title. Category is the functional domain,
such as Backend, Data Engineering, Data Science, Frontend, or DevOps.
Do not infer facts that are not supported by the posting.
""".strip()


RESUME_EXTRACTION_SYSTEM_PROMPT = """
Extract a structured profile from the resume text. Extract only information
explicitly present in the resume. Do not invent skills, experience, education,
projects, or technologies. Use empty lists when a section is absent. Use null
or an empty string for missing scalar values, according to the response schema.
Each experience item must contain company, role, duration, and description.
Each education item must contain institution, degree, field, and year. Each
project item must contain name, description, and a technologies list. Use empty
strings or empty lists for missing values within these structures. Preserve the
resume's factual meaning and return only the requested fields as JSON.
""".strip()
