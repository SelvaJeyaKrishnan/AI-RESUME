from app.ml.jd_parser import parse_job_description
from app.models.job import Job
from app.utils.json_utils import to_json


def populate_job_from_description(job: Job) -> Job:
    """Parse job.description_raw and fill in the structured JD fields on the model."""
    parsed = parse_job_description(job.description_raw, provided_title=job.title)
    job.title = job.title or parsed.title or "Untitled Role"
    job.required_skills = to_json(parsed.required_skills)
    job.preferred_skills = to_json(parsed.preferred_skills)
    job.required_experience_years = parsed.required_experience_years
    job.education_requirement = parsed.education_requirement
    job.keywords = to_json(parsed.keywords)
    job.responsibilities = to_json(parsed.responsibilities)
    return job
