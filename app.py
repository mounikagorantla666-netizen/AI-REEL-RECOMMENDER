from flask import Flask, render_template, request, jsonify
import json
from services.gemini import analyze_student_interest
from services.recommender import recommend_reel

app = Flask(__name__)


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def home():
    reels = load_json("data/reels.json")
    return render_template("index.html", reels=reels)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    reels = data.get("reels", [])

    if not reels:
        return jsonify({"success": False, "error": "No Reel data received"}), 400

    try:
        interest = analyze_student_interest(reels)
        recommendation = recommend_reel(reels)

        return jsonify({
            "success": True,
            "interest": interest,
            "recommendation": recommendation
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
