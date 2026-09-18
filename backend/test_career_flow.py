"""End-to-end test of the candidate career-report flow."""
import json
import uuid
from fastapi.testclient import TestClient
from app.main import app

RESUME = b"""SELVA JEYAKRISHNAN
selva72007@gmail.com
+91 98765 43210
Coimbatore, India

Experience
Software Engineering Intern, TechCorp
Jun 2023 - Dec 2023
- Worked on backend features using Python and Flask
- Responsible for writing SQL queries
- Helped with bug fixes

Education
Bachelor of Engineering in Computer Science, Anna University, 2024

Skills
Python, Flask, SQL, Git, Machine Learning

Projects
Resume screening tool using Flask and SQLite
"""

JD = """Python Developer

We are looking for a Python Developer with 2+ years of experience.
Required skills: Python, FastAPI, SQL, REST API, Git, Docker
Preferred: AWS, Machine Learning, PostgreSQL

Responsibilities:
- Build and maintain backend APIs
- Write tested, maintainable code

Education: Bachelor's degree in Computer Science.
"""

TEST_EMAIL = f"selva-{uuid.uuid4().hex}@test.com"

def main():
    with TestClient(app) as c:
        r = c.post('/auth/register', json={'email': TEST_EMAIL, 'password': 'password123', 'full_name': 'Selva'})
        assert r.status_code == 201, r.text
        h = {'Authorization': f"Bearer {r.json()['access_token']}"}
        print("PASS register")

        # Create report
        r = c.post('/career/reports',
                   files={'file': ('selva.txt', RESUME, 'text/plain')},
                   data={'job_description': JD, 'job_title': 'Python Developer'},
                   headers=h)
        assert r.status_code == 201, r.text
        data = r.json()
        report_id = data['report_id']
        print("PASS create report:", json.dumps(data, indent=2)[:400])
        assert 'overall_score' not in data, "Scores leaked before assessment!"
        print("PASS no scores leaked in creation response")

        # GATING: report must be locked
        r = c.get(f'/career/reports/{report_id}', headers=h)
        assert r.status_code == 403, f"Expected 403, got {r.status_code}"
        print("PASS report is gated (403):", r.json()['detail'])

        # Get assessment
        r = c.get(f'/career/reports/{report_id}/assessment', headers=h)
        assert r.status_code == 200, r.text
        qs = r.json()['questions']
        print(f"PASS got {len(qs)} questions")
        raw = r.text
        assert '"correct"' not in raw and 'explanation' not in raw, "Answer leaked in assessment payload!"
        print("PASS no answers/explanations leaked to client")

        # Answer all
        correct_count = 0
        for q in qs:
            pick = q['options'][0]['id']
            r = c.post(f'/career/reports/{report_id}/assessment/answer',
                       json={'question_id': q['id'], 'option_id': pick}, headers=h)
            assert r.status_code == 200, r.text
            fb = r.json()
            if fb['correct']:
                correct_count += 1
            assert 'explanation' in fb and fb['explanation']
        print(f"PASS answered all 5, feedback+explanations returned ({correct_count} correct)")

        # Duplicate answer blocked
        r = c.post(f'/career/reports/{report_id}/assessment/answer',
                   json={'question_id': qs[0]['id'], 'option_id': qs[0]['options'][1]['id']}, headers=h)
        assert r.status_code == 409, f"Duplicate should be 409, got {r.status_code}"
        print("PASS duplicate answer rejected (409)")

        # Complete
        r = c.post(f'/career/reports/{report_id}/assessment/complete', headers=h)
        assert r.status_code == 200, r.text
        res = r.json()
        print("PASS assessment complete:", res['correct'], '/', res['total'], res['band'])

        # Idempotent completion
        r2 = c.post(f'/career/reports/{report_id}/assessment/complete', headers=h)
        assert r2.status_code == 200 and r2.json()['already_completed'] is True
        print("PASS completing twice is idempotent")

        # Now report unlocks
        r = c.get(f'/career/reports/{report_id}', headers=h)
        assert r.status_code == 200, r.text
        rep = r.json()
        print("PASS report unlocked")
        print("  overall:", rep['overall_score'], "ats:", rep['ats_score'], "job_match:", rep['job_match_score'])
        print("  ats factors:", [(f['key'], f['score']) for f in rep['ats']['factors']])
        print("  ratings:", [(x['label'], x['score']) for x in rep['ratings']])
        print("  top roles:", [(x['role'], x['match_percent']) for x in rep['roles'][:4]])
        print("  skills have:", rep['skill_gap']['have'])
        print("  missing required:", rep['skill_gap']['missing_required'])
        print("  tips:", [(t['title'], t['priority']) for t in rep['tips']])
        print("  communication:", rep['communication'])
        assert rep['ats_score'] > 0 and rep['overall_score'] > 0
        assert len(rep['roles']) > 0
        assert len(rep['tips']) > 0
        # verify a tip has a real before/after from the user's own resume
        ba = [t for t in rep['tips'] if t.get('before')]
        if ba:
            print("  BEFORE:", ba[0]['before'])
            print("  AFTER :", ba[0]['after'])

        # Validation: empty JD
        r = c.post('/career/reports', files={'file': ('x.txt', RESUME, 'text/plain')},
                   data={'job_description': 'short'}, headers=h)
        assert r.status_code == 400, r.status_code
        print("PASS empty/short JD rejected with friendly message:", r.json()['detail'][:60])

        # Validation: bad file type
        r = c.post('/career/reports', files={'file': ('x.exe', b'MZ\x00binary', 'application/octet-stream')},
                   data={'job_description': JD}, headers=h)
        assert r.status_code == 415, r.status_code
        print("PASS unsupported file type rejected (415)")

        # List reports
        r = c.get('/career/reports', headers=h)
        assert r.status_code == 200 and len(r.json()) >= 1
        print("PASS list reports:", len(r.json()))

        # Recruiter flow still works
        r = c.post('/jobs', json={'title': 'Backend Dev', 'description_raw': JD}, headers=h)
        assert r.status_code == 201, r.text
        print("PASS legacy recruiter job endpoint still works")
        r = c.get('/resumes', headers=h)
        assert r.status_code == 200
        print("PASS legacy resumes endpoint still works:", len(r.json()), "resumes")

        print("\n=== ALL BACKEND TESTS PASSED ===")

main()
