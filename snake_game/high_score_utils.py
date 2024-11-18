import json

HIGH_SCORES_FILE = "high_scores.json"


def read_high_scores():
    try:
        with open(HIGH_SCORES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def update_high_scores(score, name):
    high_scores = read_high_scores()
    high_scores.append({"name": name, "score": score})
    # Keep only the top 5 scores
    high_scores = sorted(high_scores, key=lambda x: x["score"], reverse=True)[:5]
    with open(HIGH_SCORES_FILE, "w") as f:
        json.dump(high_scores, f)
