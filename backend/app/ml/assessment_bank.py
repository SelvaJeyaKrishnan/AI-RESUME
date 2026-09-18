"""
Communication & grammar assessment question bank.

Questions are stored server-side with their correct answers and explanations.
The API never sends `correct_option_id` or `explanation` to the client before
the user has submitted an answer for that question — this is what prevents the
answer being readable from the network tab or React state.
"""
import random

# category: grammar | communication
QUESTION_BANK: list[dict] = [
    {
        "id": "g1",
        "category": "grammar",
        "skill": "Tense consistency",
        "prompt": "Which sentence is grammatically correct?",
        "options": [
            {"id": "a", "text": "I have completed my project yesterday."},
            {"id": "b", "text": "I completed my project yesterday."},
            {"id": "c", "text": "I has completed my project yesterday."},
            {"id": "d", "text": "I completing my project yesterday."},
        ],
        "correct": "b",
        "explanation": "'Yesterday' points to a finished moment in the past, so the simple past ('completed') is correct. "
                        "The present perfect ('have completed') can't be paired with a specific past time reference.",
    },
    {
        "id": "g2",
        "category": "grammar",
        "skill": "Subject–verb agreement",
        "prompt": "Choose the sentence with correct subject–verb agreement.",
        "options": [
            {"id": "a", "text": "The team of developers are working on the release."},
            {"id": "b", "text": "The team of developers is working on the release."},
            {"id": "c", "text": "The team of developers were working on the release."},
            {"id": "d", "text": "The team of developers been working on the release."},
        ],
        "correct": "b",
        "explanation": "The subject is 'team' (singular), not 'developers'. The phrase 'of developers' is a modifier, "
                        "so the verb agrees with 'team' and takes 'is'.",
    },
    {
        "id": "g3",
        "category": "grammar",
        "skill": "Articles",
        "prompt": "Which sentence uses articles correctly?",
        "options": [
            {"id": "a", "text": "I am applying for a engineering role at an startup."},
            {"id": "b", "text": "I am applying for an engineering role at a startup."},
            {"id": "c", "text": "I am applying for the engineering role at an startup."},
            {"id": "d", "text": "I am applying for an engineering role at an startup."},
        ],
        "correct": "b",
        "explanation": "'An' is used before a vowel sound ('engineering'), and 'a' before a consonant sound ('startup'). "
                        "It's the sound that matters, not the letter.",
    },
    {
        "id": "g4",
        "category": "grammar",
        "skill": "Prepositions",
        "prompt": "Which sentence uses the preposition correctly?",
        "options": [
            {"id": "a", "text": "I have experience in working with distributed systems."},
            {"id": "b", "text": "I have experience on working with distributed systems."},
            {"id": "c", "text": "I have experience at working with distributed systems."},
            {"id": "d", "text": "I have experience of work with distributed systems."},
        ],
        "correct": "a",
        "explanation": "The standard collocation is 'experience in' followed by a gerund ('working'). "
                        "'Experience on' and 'experience at' are not idiomatic in this construction.",
    },
    {
        "id": "g5",
        "category": "grammar",
        "skill": "Sentence structure",
        "prompt": "Which sentence is correctly structured?",
        "options": [
            {"id": "a", "text": "Because I was interested in the role, so I applied immediately."},
            {"id": "b", "text": "Because I was interested in the role, I applied immediately."},
            {"id": "c", "text": "Because I was interested in the role and I applied immediately."},
            {"id": "d", "text": "I was interested in the role, I applied immediately."},
        ],
        "correct": "b",
        "explanation": "'Because' already signals the cause, so adding 'so' duplicates the connector. "
                        "Option D is a comma splice — two independent clauses joined by only a comma.",
    },
    {
        "id": "g6",
        "category": "grammar",
        "skill": "Conditionals",
        "prompt": "Which sentence is grammatically correct?",
        "options": [
            {"id": "a", "text": "If I would have known, I would have prepared better."},
            {"id": "b", "text": "If I had known, I would have prepared better."},
            {"id": "c", "text": "If I have known, I would prepare better."},
            {"id": "d", "text": "If I knew, I would have prepared better."},
        ],
        "correct": "b",
        "explanation": "The third conditional uses 'If + past perfect, would have + past participle'. "
                        "'If I would have known' is a common but non-standard construction.",
    },
    {
        "id": "c1",
        "category": "communication",
        "skill": "Interview response",
        "prompt": "An interviewer asks about a technology you haven't used. What's the most professional response?",
        "options": [
            {"id": "a", "text": "\"I don't know that one, sorry.\""},
            {"id": "b", "text": "\"I haven't worked with it directly, but I've used a similar tool and I'd be comfortable picking it up.\""},
            {"id": "c", "text": "\"Yes, I've used it a lot.\""},
            {"id": "d", "text": "\"That's not really relevant to what I do.\""},
        ],
        "correct": "b",
        "explanation": "This is honest about the gap while showing transferable experience and willingness to learn. "
                        "Overclaiming (C) tends to unravel under follow-up questions, and A and D close the conversation down.",
    },
    {
        "id": "c2",
        "category": "communication",
        "skill": "Professional email",
        "prompt": "You need to ask your manager for a deadline extension. Which opening is most professional?",
        "options": [
            {"id": "a", "text": "\"I can't finish this on time.\""},
            {"id": "b", "text": "\"The deadline is impossible, nobody could do this.\""},
            {"id": "c", "text": "\"I want to flag a risk to Friday's deadline and propose a revised plan.\""},
            {"id": "d", "text": "\"Just letting you know it'll be late.\""},
        ],
        "correct": "c",
        "explanation": "It raises the issue early, is specific about what's at risk, and arrives with a proposed solution "
                        "rather than only a problem. That framing gives your manager something to act on.",
    },
    {
        "id": "c3",
        "category": "communication",
        "skill": "Workplace communication",
        "prompt": "You disagree with a technical decision in a team meeting. What's the most effective approach?",
        "options": [
            {"id": "a", "text": "Stay quiet and raise it privately with people who agree with you afterwards."},
            {"id": "b", "text": "Say the approach is wrong and explain why everyone else is mistaken."},
            {"id": "c", "text": "Ask about the trade-offs considered, then explain your concern with a specific alternative."},
            {"id": "d", "text": "Go along with it and document that you disagreed."},
        ],
        "correct": "c",
        "explanation": "Asking first surfaces context you may be missing, and pairing a concern with a concrete alternative "
                        "keeps the discussion technical rather than personal. Option A creates side-channels that erode trust.",
    },
    {
        "id": "c4",
        "category": "communication",
        "skill": "Professional tone",
        "prompt": "Which sentence is most appropriate for a follow-up email after an interview?",
        "options": [
            {"id": "a", "text": "\"Hey, just checking if I got the job yet??\""},
            {"id": "b", "text": "\"Thank you for your time today. I enjoyed discussing the role and I'm glad to answer any follow-up questions.\""},
            {"id": "c", "text": "\"Please let me know ASAP, I have other offers waiting.\""},
            {"id": "d", "text": "\"I assume I did well so I look forward to the offer.\""},
        ],
        "correct": "b",
        "explanation": "It's warm, specific and professional without applying pressure or presuming the outcome. "
                        "Manufactured urgency (C) and presumption (D) both tend to read poorly.",
    },
    {
        "id": "c5",
        "category": "communication",
        "skill": "Explaining your work",
        "prompt": "A non-technical stakeholder asks why a feature is delayed. What's the best response?",
        "options": [
            {"id": "a", "text": "\"We hit a race condition in the async queue consumer during deserialization.\""},
            {"id": "b", "text": "\"It's complicated, it's a technical thing.\""},
            {"id": "c", "text": "\"We found a bug that could duplicate customer orders. Fixing it properly adds two days, and I'd rather not ship a data risk.\""},
            {"id": "d", "text": "\"Engineering is behind schedule.\""},
        ],
        "correct": "c",
        "explanation": "It translates the technical problem into business impact, gives a concrete timeline, and explains "
                        "the reasoning. Option A assumes technical vocabulary; B and D give the stakeholder nothing to work with.",
    },
    {
        "id": "c6",
        "category": "communication",
        "skill": "Receiving feedback",
        "prompt": "You receive critical feedback on your code in a review. What's the most professional reply?",
        "options": [
            {"id": "a", "text": "\"That's how I've always done it.\""},
            {"id": "b", "text": "\"Good points — I'll address the error handling. Could you say more about the naming concern?\""},
            {"id": "c", "text": "\"Fine, I'll change it.\""},
            {"id": "d", "text": "\"You didn't understand what I was trying to do.\""},
        ],
        "correct": "b",
        "explanation": "It accepts the actionable feedback, commits to a specific fix, and asks a clarifying question "
                        "about the part that isn't clear — which keeps the review collaborative rather than defensive.",
    },
]

QUESTIONS_PER_ASSESSMENT = 5


def build_assessment(seed: str | None = None) -> list[dict]:
    """Select a balanced, randomised set of questions with shuffled options.

    Returns the FULL question dicts (including answers) for server-side storage.
    Use `public_question` before sending any of this to the client.
    """
    rng = random.Random(seed)
    grammar = [q for q in QUESTION_BANK if q["category"] == "grammar"]
    communication = [q for q in QUESTION_BANK if q["category"] == "communication"]

    # Aim for a 3/2 grammar/communication split out of 5
    picked = rng.sample(grammar, min(3, len(grammar))) + rng.sample(communication, min(2, len(communication)))
    rng.shuffle(picked)

    prepared = []
    for q in picked[:QUESTIONS_PER_ASSESSMENT]:
        options = q["options"][:]
        rng.shuffle(options)
        prepared.append({**q, "options": options})
    return prepared


def public_question(question: dict, index: int, total: int) -> dict:
    """Strip the correct answer and explanation before sending to the client."""
    return {
        "id": question["id"],
        "index": index,
        "total": total,
        "category": question["category"],
        "skill": question["skill"],
        "prompt": question["prompt"],
        "options": [{"id": o["id"], "text": o["text"]} for o in question["options"]],
    }


def score_band(correct: int, total: int) -> tuple[str, str]:
    """Return (label, message) for a completed assessment. Deliberately measured
    language — a 5-question test does not justify sweeping claims."""
    pct = (correct / total * 100) if total else 0
    if pct >= 80:
        return ("Strong", "Great work. Your communication fundamentals are looking good on this short check.")
    if pct >= 60:
        return ("Good", "You have a good foundation. A little polish on grammar and professional phrasing would "
                         "strengthen how you come across in interviews.")
    return ("Developing", "There's room to grow here. Improving grammar and professional communication could "
                           "meaningfully strengthen your interview performance. This is a short 5-question check, "
                           "not a definitive measure.")
