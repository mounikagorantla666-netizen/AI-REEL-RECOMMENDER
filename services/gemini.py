import os
from dotenv import load_dotenv

load_dotenv()

MODEL = "gemini-2.5-flash"


def _get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    from google import genai
    return genai.Client(api_key=api_key)


def _local_interest(reels):
    """Always-available fallback so the demo remains interactive without Gemini."""
    if not reels:
        return "No interaction data available."

    scores = {}
    for reel in reels:
        category = reel.get("category", "Other")
        watch = float(reel.get("watch_percentage", 0))
        liked = 1 if reel.get("liked") else 0
        saved = 2 if reel.get("saved") else 0
        shared = 2 if reel.get("shared") else 0
        score = watch + liked * 15 + saved * 25 + shared * 25
        scores[category] = scores.get(category, 0) + score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    main = ranked[0][0] if ranked else "Technology"
    secondary = [x[0] for x in ranked[1:3]]

    return (
        f"Main interest: {main}\n"
        f"Secondary interests: {', '.join(secondary) if secondary else 'General technology'}\n"
        "Learning intent: Practical and career-oriented learning\n"
        "Evidence: High watch time plus likes, saves and shares on related Reels\n"
        "Confidence: Medium"
    )


def analyze_student_interest(reels):
    client = _get_client()

    if client is None:
        return _local_interest(reels)

    prompt = f"""
You are an AI recommendation agent for students.

Analyze the student's Reel interaction history.
Do NOT use simple keyword matching.

Infer the student's broader underlying interests using:
- topic
- context
- watch percentage
- likes
- saves
- shares
- repeated themes
- learning intent
- career intent

Identify:
1. Main interest
2. Secondary interests
3. Learning intent
4. Evidence
5. Confidence

Student Reel history:
{reels}

Give a clear and concise analysis.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception:
        # Keep the web app usable even if Gemini is temporarily unavailable.
        return _local_interest(reels)
