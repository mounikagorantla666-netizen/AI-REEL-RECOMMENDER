AI Reel Recommender - Interactive Flask Web App

1. Create/activate a virtual environment.
2. Install:
   pip install -r requirements.txt
3. Optional Gemini AI:
   - Copy .env.example to .env
   - Put your Google AI Studio API key in GEMINI_API_KEY.
   - The app still works without a key using a local fallback.
4. Run:
   python app.py
5. Open:
   http://127.0.0.1:5000

Interact with the Reel cards:
- move Watch %
- Like / Save / Share
- click Watch Reel
- click Analyze My Reels

The current behavior is sent to /analyze and used to produce an interest profile and recommendation.
