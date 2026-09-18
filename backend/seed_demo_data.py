"""
Seeds the database with a demo recruiter account, one job description,
and five sample resumes with genuinely different skill sets/experience
levels, then runs the real AI matching pipeline against them so the
dashboard is immediately useful after setup.

Run with:  python seed_demo_data.py
"""
from app.database.session import Base, engine, SessionLocal
from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume
from app.services.job_service import populate_job_from_description
from app.services.resume_service import process_resume
from app.services.analysis_service import run_analysis
from app.utils.file_handling import save_upload, compute_file_hash
from app.utils.security import hash_password

DEMO_EMAIL = "demo@resumeai.com"
DEMO_PASSWORD = "demopassword123"

JOB_DESCRIPTION = """Senior Full-Stack Engineer

We're hiring a Senior Full-Stack Engineer with 4+ years of experience to join our
growing product team. You'll work across our Python/FastAPI backend and React
frontend, owning features end to end.

Required skills: Python, FastAPI, React, PostgreSQL, REST API, Git, Docker
Preferred: AWS, Kubernetes, TypeScript, Machine Learning, GraphQL

Responsibilities:
- Design and build scalable backend services and APIs
- Build responsive, accessible React interfaces
- Collaborate closely with product and design
- Write tests and participate in code review
- Mentor junior engineers

Education: Bachelor's degree in Computer Science or related field, or equivalent experience.
"""

CANDIDATES = [
    {
        "filename": "aisha_khan.txt",
        "text": """Aisha Khan
aisha.khan@email.com
+1 415-555-0142
Seattle, WA

Summary
Full-stack engineer with 6 years of experience shipping production web applications.

Experience
Senior Software Engineer, Northwind Labs
Mar 2021 - Present
- Led backend development using Python, FastAPI and PostgreSQL
- Built React + TypeScript frontend for the core product dashboard
- Deployed services with Docker and AWS ECS
- Introduced CI/CD pipelines with GitHub Actions

Software Engineer, Riverstone Tech
Jul 2018 - Feb 2021
- Built REST APIs in Django and Flask
- Worked with PostgreSQL and Redis
- Used Git for version control across a 12-engineer team

Education
Bachelor of Science in Computer Science, University of Washington, 2018

Skills
Python, FastAPI, Django, React, TypeScript, PostgreSQL, Docker, AWS, Git, REST API, GraphQL

Certifications
AWS Certified Solutions Architect
""",
    },
    {
        "filename": "marcus_lee.txt",
        "text": """Marcus Lee
marcus.lee@email.com
(312) 555-0198
Chicago, IL

Summary
Backend-focused engineer with 3 years of experience in Python services.

Experience
Software Engineer, DataForge Inc
Jan 2022 - Present
- Built internal REST APIs using FastAPI and PostgreSQL
- Wrote unit tests with pytest
- Used Git and participated in code reviews

Junior Developer, StartUpXYZ
Jun 2021 - Dec 2021
- Assisted with Python scripting and data pipelines

Education
Bachelor of Science in Information Technology, DePaul University, 2021

Skills
Python, FastAPI, PostgreSQL, Git, REST API, Unit Testing

Projects
Personal finance tracker built with Flask and SQLite
""",
    },
    {
        "filename": "priya_sharma.txt",
        "text": """Priya Sharma
priya.sharma@email.com
+91 98765 43210
Bangalore, India

Summary
Frontend engineer with 5 years of experience specializing in React applications.

Experience
Senior Frontend Engineer, PixelWorks
Apr 2020 - Present
- Built and maintained large-scale React and TypeScript applications
- Collaborated with backend teams consuming REST and GraphQL APIs
- Used Git and Agile/Scrum practices

Frontend Developer, WebCrafters
Feb 2018 - Mar 2020
- Developed responsive UIs with React and Redux
- Worked with Node.js for lightweight backend services

Education
Master of Computer Applications, Bangalore University, 2018

Skills
React, TypeScript, JavaScript, Redux, Node.js, GraphQL, Git, HTML/CSS, Agile/Scrum

Certifications
Meta React Developer Certificate
""",
    },
    {
        "filename": "daniel_osei.txt",
        "text": """Daniel Osei
daniel.osei@email.com
+44 7700 900123
London, UK

Summary
Machine learning engineer with 4 years of experience building ML-powered products.

Experience
ML Engineer, Insight Analytics
Sep 2021 - Present
- Built ML pipelines using Python, scikit-learn, and TensorFlow
- Deployed models behind FastAPI services on AWS
- Used Docker and Kubernetes for deployment
- Worked with PostgreSQL for feature storage

Data Scientist, QuantEdge
Jul 2019 - Aug 2021
- Built predictive models using Python and pandas
- Presented findings using data visualization tools

Education
Master of Science in Data Science, Imperial College London, 2019

Skills
Python, Machine Learning, TensorFlow, scikit-learn, FastAPI, Docker, Kubernetes, AWS, PostgreSQL, Pandas

Certifications
AWS Certified Machine Learning - Specialty
""",
    },
    {
        "filename": "grace_okafor.txt",
        "text": """Grace Okafor
grace.okafor@email.com
+1 646-555-0177
New York, NY

Summary
Recent computer science graduate with internship experience in web development.

Experience
Software Engineering Intern, BrightPath Startups
Jun 2023 - Aug 2023
- Built small features in a Django web application
- Wrote basic unit tests
- Assisted with bug fixes and documentation

Education
Bachelor of Science in Computer Science, Columbia University, 2024

Skills
Python, Django, HTML/CSS, Git, SQL

Projects
Built a to-do list app using Flask and SQLite
Contributed to an open-source documentation project
""",
    },
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if not user:
            user = User(
                email=DEMO_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
                full_name="Demo Recruiter",
                company_name="ResumeAI Demo Co.",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print("Demo user already exists, reusing it.")

        job = db.query(Job).filter(Job.owner_id == user.id, Job.title == "Senior Full-Stack Engineer").first()
        if not job:
            job = Job(owner_id=user.id, title="Senior Full-Stack Engineer", description_raw=JOB_DESCRIPTION)
            job = populate_job_from_description(job)
            db.add(job)
            db.commit()
            db.refresh(job)
            print(f"Created demo job: {job.title} ({job.id})")
        else:
            print("Demo job already exists, reusing it.")

        for c in CANDIDATES:
            contents = c["text"].encode("utf-8")
            file_hash = compute_file_hash(contents)
            existing = db.query(Resume).filter(Resume.owner_id == user.id, Resume.file_hash == file_hash).first()
            if existing:
                print(f"  Skipping {c['filename']} (already seeded)")
                resume = existing
            else:
                stored_path = save_upload(contents, ".txt", user.id)
                resume = Resume(
                    owner_id=user.id,
                    original_filename=c["filename"],
                    stored_path=stored_path,
                    file_type="txt",
                    file_hash=file_hash,
                )
                db.add(resume)
                db.commit()
                db.refresh(resume)
                resume = process_resume(db, resume, contents)
                print(f"  Parsed {c['filename']} -> status={resume.parse_status}")

            if resume.parse_status == "success":
                analysis = run_analysis(db, resume, job)
                print(f"    Score vs job: {analysis.overall_score} ({analysis.recommendation})")

        print("\nDemo data ready. Log in with:")
        print(f"  email:    {DEMO_EMAIL}")
        print(f"  password: {DEMO_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
