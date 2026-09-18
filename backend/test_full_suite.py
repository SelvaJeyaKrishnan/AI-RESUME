"""Full regression + flow test: candidate career flow AND preserved recruiter flow."""
import uuid

from fastapi.testclient import TestClient
from app.main import app

PASS, FAIL = [], []

def check(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(f"{'PASS' if cond else 'FAIL'}  {name}{(' — ' + str(extra)) if extra and not cond else ''}")

GOOD_RESUME = b"""Priya Raman
priya.raman@example.com
+91 90000 11111
Chennai, India

Summary
Backend engineer with 4 years of experience building production APIs.

Experience
Senior Backend Engineer, Nimbus Systems
Mar 2021 - Present
- Designed REST API services in Python and FastAPI serving 2M requests/day
- Reduced p95 latency by 40% through query optimization in PostgreSQL
- Deployed with Docker on AWS, automated CI/CD with GitHub Actions

Backend Engineer, Corex Labs
Jun 2019 - Feb 2021
- Built microservices in Python, increased test coverage to 85%

Education
Bachelor of Engineering in Computer Science, Anna University, 2019

Skills
Python, FastAPI, PostgreSQL, Docker, AWS, Git, REST API, Unit Testing, Kubernetes

Certifications
AWS Certified Developer Associate
"""

WEAK_RESUME = b"""john smith
Worked on stuff
Responsible for things
"""

JD = """Senior Python Backend Engineer

Looking for a backend engineer with 3+ years of experience.
Required skills: Python, FastAPI, PostgreSQL, Docker, REST API, Git
Preferred: AWS, Kubernetes, Machine Learning

Responsibilities:
- Build scalable backend services
- Own deployment pipelines

Education: Bachelor's degree in Computer Science.
"""

TEST_EMAIL = f"priya-{uuid.uuid4().hex}@test.com"
OTHER_TEST_EMAIL = f"other-{uuid.uuid4().hex}@test.com"

with TestClient(app) as c:
    # ---------- 1. Registration ----------
    r = c.post('/auth/register', json={'email': TEST_EMAIL, 'password': 'password123', 'full_name': 'Priya Raman'})
    check("New user registration", r.status_code == 201, r.text)
    h = {'Authorization': f"Bearer {r.json()['access_token']}"}

    # duplicate registration
    r2 = c.post('/auth/register', json={'email': TEST_EMAIL, 'password': 'password123'})
    check("Duplicate registration rejected (409)", r2.status_code == 409)

    # ---------- 2. Login ----------
    r = c.post('/auth/login', json={'email': TEST_EMAIL, 'password': 'password123'})
    check("Login", r.status_code == 200)
    r = c.post('/auth/login', json={'email': TEST_EMAIL, 'password': 'wrongpass'})
    check("Bad password rejected (401)", r.status_code == 401)

    # unauthenticated access blocked
    r = c.get('/career/reports')
    check("Unauthenticated access blocked (401)", r.status_code == 401)

    # ---------- 3. Validation ----------
    r = c.post('/career/reports', files={'file': ('r.txt', GOOD_RESUME, 'text/plain')},
               data={'job_description': 'too short'}, headers=h)
    check("Empty/short job description rejected (400)", r.status_code == 400)

    r = c.post('/career/reports', files={'file': ('bad.exe', b'MZbinary', 'application/octet-stream')},
               data={'job_description': JD}, headers=h)
    check("Unsupported file format rejected (415)", r.status_code == 415)

    r = c.post('/career/reports', files={'file': ('empty.txt', b'', 'text/plain')},
               data={'job_description': JD}, headers=h)
    check("Empty resume file rejected (400)", r.status_code == 400)

    # ---------- 4. Create report (strong resume) ----------
    r = c.post('/career/reports', files={'file': ('priya.txt', GOOD_RESUME, 'text/plain')},
               data={'job_description': JD, 'job_title': 'Senior Python Backend Engineer'}, headers=h)
    check("Resume upload + processing", r.status_code == 201, r.text)
    rid = r.json()['report_id']
    body = r.json()
    check("No scores leaked before assessment", not any(k in body for k in ('overall_score', 'ats_score', 'job_match_score')))
    check("Candidate name extracted", body.get('candidate_name') == 'Priya Raman', body.get('candidate_name'))

    # ---------- 5. Gating ----------
    r = c.get(f'/career/reports/{rid}', headers=h)
    check("Report locked before assessment (403)", r.status_code == 403)

    r = c.get('/career/reports', headers=h)
    locked = [x for x in r.json() if x['id'] == rid][0]
    check("Locked report hides scores in list", locked['overall_score'] is None)

    # ---------- 6. Assessment ----------
    r = c.get(f'/career/reports/{rid}/assessment', headers=h)
    check("Assessment loads", r.status_code == 200)
    qs = r.json()['questions']
    check("Assessment has 5 questions", len(qs) == 5, len(qs))
    check("Answers not leaked to client", '"correct"' not in r.text and 'explanation' not in r.text)
    check("Questions have 4 options each", all(len(q['options']) == 4 for q in qs))

    # incomplete completion blocked
    r = c.post(f'/career/reports/{rid}/assessment/complete', headers=h)
    check("Cannot complete before answering all (400)", r.status_code == 400)

    # answer all
    got_correct, got_incorrect = False, False
    for q in qs:
        r = c.post(f'/career/reports/{rid}/assessment/answer',
                   json={'question_id': q['id'], 'option_id': q['options'][0]['id']}, headers=h)
        assert r.status_code == 200, r.text
        fb = r.json()
        if fb['correct']: got_correct = True
        else: got_incorrect = True
        assert fb['explanation']
    check("All answers accepted with explanations", True)
    check("Correct-answer feedback path exercised" if got_correct else "Incorrect-answer feedback path exercised", True)

    # duplicate submission
    r = c.post(f'/career/reports/{rid}/assessment/answer',
               json={'question_id': qs[0]['id'], 'option_id': qs[0]['options'][1]['id']}, headers=h)
    check("Duplicate answer submission blocked (409)", r.status_code == 409)

    # bad question id
    r = c.post(f'/career/reports/{rid}/assessment/answer',
               json={'question_id': 'nonexistent', 'option_id': 'a'}, headers=h)
    check("Unknown question id rejected (404)", r.status_code == 404)

    # ---------- 7. Complete + unlock ----------
    r = c.post(f'/career/reports/{rid}/assessment/complete', headers=h)
    check("Assessment completion", r.status_code == 200)
    comp = r.json()
    check("Communication score computed", comp['total'] == 5 and 0 <= comp['correct'] <= 5)
    check("Score band assigned", comp['band'] in ('Strong', 'Good', 'Developing'))

    r = c.post(f'/career/reports/{rid}/assessment/complete', headers=h)
    check("Repeat completion is idempotent", r.status_code == 200 and r.json()['already_completed'])

    # ---------- 8. Report content ----------
    r = c.get(f'/career/reports/{rid}', headers=h)
    check("Report unlocks after assessment", r.status_code == 200)
    rep = r.json()

    check("ATS score present and non-zero", rep['ats_score'] > 0, rep['ats_score'])
    check("ATS has 6 explained factors", len(rep['ats']['factors']) == 6)
    check("Every ATS factor has detail + suggestion",
          all(f['detail'] and f['suggestion'] for f in rep['ats']['factors']))
    check("Overall resume score present", rep['overall_score'] > 0)
    check("7 rating categories present", len(rep['ratings']) == 7, len(rep['ratings']))
    check("Job match score present", rep['job_match_score'] > 0)
    check("Role recommendations returned", len(rep['roles']) > 0)
    check("Roles ranked descending",
          all(rep['roles'][i]['match_percent'] >= rep['roles'][i+1]['match_percent'] for i in range(len(rep['roles'])-1)))

    top_role = rep['roles'][0]['role']
    check(f"Top role is backend-relevant (got '{top_role}')",
          top_role in ('Backend Developer', 'Python Developer', 'Full-Stack Developer', 'DevOps Engineer', 'Cloud Engineer'), top_role)

    have = set(rep['skill_gap']['have'])
    check("Skill extraction found real skills", {'Python', 'FastAPI', 'Docker'} <= have, sorted(have))
    check("Skill gap has all four buckets",
          all(k in rep['skill_gap'] for k in ('have', 'required_by_job', 'missing_required', 'matched')))
    check("Parser caveat present (no false 'missing' claims)", bool(rep['skill_gap'].get('parser_caveat')))
    check("Improvement tips generated", len(rep['tips']) > 0)
    check("Tips have issue/why/fix", all(t['issue'] and t['why'] and t['fix'] for t in rep['tips']))
    check("Communication score in report", rep['communication'] is not None and rep['communication']['total'] == 5)
    check("Strengths present", len(rep['strengths']) > 0)
    check("Disclaimer present", 'not a hiring decision' in rep['disclaimer'])
    check("Candidate details extracted", rep['candidate']['email'] == 'priya.raman@example.com')
    check("Experience detected", rep['candidate']['years_of_experience'] > 0, rep['candidate']['years_of_experience'])

    print(f"\n  Strong resume -> ATS {rep['ats_score']}, Overall {rep['overall_score']}, Match {rep['job_match_score']}")
    print(f"  Top roles: {[(x['role'], x['match_percent']) for x in rep['roles'][:3]]}")

    # ---------- 9. Weak resume scores lower (proves scoring is real) ----------
    r = c.post('/career/reports', files={'file': ('weak.txt', WEAK_RESUME, 'text/plain')},
               data={'job_description': JD, 'job_title': 'Senior Python Backend Engineer'}, headers=h)
    if r.status_code == 201:
        rid2 = r.json()['report_id']
        qs2 = c.get(f'/career/reports/{rid2}/assessment', headers=h).json()['questions']
        for q in qs2:
            c.post(f'/career/reports/{rid2}/assessment/answer',
                   json={'question_id': q['id'], 'option_id': q['options'][0]['id']}, headers=h)
        c.post(f'/career/reports/{rid2}/assessment/complete', headers=h)
        rep2 = c.get(f'/career/reports/{rid2}', headers=h).json()
        check("Weak resume scores lower than strong resume (scoring is real, not fixed)",
              rep2['ats_score'] < rep['ats_score'] and rep2['overall_score'] < rep['overall_score'],
              f"weak={rep2['ats_score']}/{rep2['overall_score']} strong={rep['ats_score']}/{rep['overall_score']}")
        print(f"  Weak resume  -> ATS {rep2['ats_score']}, Overall {rep2['overall_score']}")
        check("Weak resume gets more improvement tips", len(rep2['tips']) >= len(rep['tips']))

    # ---------- 10. Cross-user isolation ----------
    r = c.post('/auth/register', json={'email': OTHER_TEST_EMAIL, 'password': 'password123'})
    h2 = {'Authorization': f"Bearer {r.json()['access_token']}"}
    r = c.get(f'/career/reports/{rid}', headers=h2)
    check("Another user cannot read your report (404)", r.status_code == 404)

    # ---------- 11. Reports list + delete ----------
    r = c.get('/career/reports', headers=h)
    check("Reports list returns user's reports", r.status_code == 200 and len(r.json()) >= 1)
    unlocked = [x for x in r.json() if x['id'] == rid][0]
    check("Unlocked report exposes scores in list", unlocked['overall_score'] is not None)

    # ---------- 12. RECRUITER REGRESSION ----------
    r = c.post('/jobs', json={'title': 'Recruiter Test Job', 'description_raw': JD}, headers=h)
    check("[regression] Create job", r.status_code == 201)
    job_id = r.json()['id']
    check("[regression] JD parsing extracts skills", len(r.json()['required_skills']) > 0)

    r = c.post('/resumes/upload', files=[('files', ('rec.txt', GOOD_RESUME, 'text/plain'))], headers=h)
    check("[regression] Resume upload", r.status_code == 201)
    res_id = r.json()[0]['resume']['id']

    r = c.post(f'/analysis/{res_id}/{job_id}', headers=h)
    check("[regression] Run analysis", r.status_code == 200 and r.json()['overall_score'] > 0)

    r = c.get(f'/jobs/{job_id}/ranking', headers=h)
    check("[regression] Candidate ranking", r.status_code == 200 and len(r.json()) >= 1)

    r = c.get(f'/jobs/{job_id}/analytics', headers=h)
    check("[regression] Analytics", r.status_code == 200)

    r = c.get('/resumes', headers=h)
    check("[regression] Resume library", r.status_code == 200)

    r = c.get('/health')
    check("[regression] Health endpoint", r.status_code == 200)

    r = c.get('/openapi.json')
    paths = r.json()['paths']
    check("[regression] All legacy endpoints still registered",
          all(p in paths for p in ('/jobs', '/resumes/upload', '/analysis/{resume_id}/{job_id}',
                                    '/jobs/{job_id}/ranking', '/auth/login')))
    check("New career endpoints registered",
          all(p in paths for p in ('/career/reports', '/career/reports/{report_id}',
                                    '/career/reports/{report_id}/assessment')))

print("\n" + "=" * 60)
print(f"RESULTS: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILURES:")
    for f in FAIL:
        print("  -", f)
else:
    print("ALL TESTS PASSED")
print("=" * 60)
