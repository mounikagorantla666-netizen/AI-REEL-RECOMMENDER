import json
import os
from dotenv import load_dotenv

load_dotenv()

MODEL = "gemini-2.5-flash"


def _load_candidates():
    with open("data/candidate_reels.json", "r", encoding="utf-8") as file:
        return json.load(file)


def _local_recommendation(student_reels):
    candidates = _load_candidates()
    if not candidates:
        return "No candidate technology Reel is available."

    scores = {}
    for reel in student_reels:
        category = reel.get("category", "Other")
        watch = float(reel.get("watch_percentage", 0))
        engagement = (
            (1 if reel.get("liked") else 0) * 15
            + (1 if reel.get("saved") else 0) * 25
            + (1 if reel.get("shared") else 0) * 25
        )
        scores[category] = scores.get(category, 0) + watch + engagement

    preferred = max(scores, key=scores.get) if scores else "Software Development"

    def candidate_score(c):
        title = c.get("title", "").lower()
        category = c.get("category", "")
        score = 0
        if category == preferred:
            score += 100
        if preferred.lower() in title:
            score += 20
        return score

    best = max(candidates, key=candidate_score)

    return f"""CURRENT REEL: {student_reels[0].get("title", "Current Reel")}

INTEREST DETECTED: {preferred}

WHY: The student's strongest engagement is around {preferred.lower()} content.

RECOMMENDED TECH REEL: {best.get("title")}

CATEGORY: {best.get("category", "Other")}

WHY THIS RECOMMENDATION: It matches the strongest observed interaction pattern while providing practical technology learning value.

DIFFICULTY: {best.get("difficulty", "Intermediate")}

CONFIDENCE: Medium"""


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    from google import genai
    return genai.Client(api_key=api_key)


def recommend_reel(student_reels):
    candidates = _load_candidates()
    client = _get_client()

    if client is None:
        return _local_recommendation(student_reels)

    prompt = f"""
You are an AI-powered technology Reel recommendation agent.

You have:
1. A student's Reel interaction history
2. A list of candidate technology Reels

Infer the student's BROADER underlying interest.
Do NOT recommend based only on matching keywords.

Consider:
- topic
- context
- watch percentage
- likes
- saves
- shares
- repeated themes
- learning intent
- career intent

Avoid hype, clickbait and unrealistic career claims.

Choose ONE best technology Reel.

STUDENT REELS:
{json.dumps(student_reels, indent=2)}

CANDIDATE TECHNOLOGY REELS:
{json.dumps(candidates, indent=2)}

Return EXACTLY in this format:

CURRENT REEL: [title]

INTEREST DETECTED: [broader interest]

WHY: [evidence from student's Reel history]

RECOMMENDED TECH REEL: [title]

CATEGORY: [AI / DSA / Java / HLD / Cybersecurity / Cloud / Hardware / Career / Other]

WHY THIS RECOMMENDATION: [connection between interest and recommendation]

DIFFICULTY: [Beginner / Intermediate / Advanced]

CONFIDENCE: [High / Medium / Low]
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception:
        return _local_recommendation(student_reels)
