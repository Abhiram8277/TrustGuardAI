from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

history = []

user_profile = {
    "total_scans": 0,
    "high_risk": 0,
    "medium_risk": 0,
    "safe": 0
}

def get_target_status():
    total = user_profile["total_scans"]
    high = user_profile["high_risk"]
    medium = user_profile["medium_risk"]

    if total == 0:
        return "No activity yet", 100

    risk_ratio = (high * 2 + medium) / total

    if risk_ratio > 1:
        return "You are being actively targeted", 30
    elif risk_ratio > 0.5:
        return "Suspicious activity detected", 60
    else:
        return "Normal activity", 90

def analyze_text(text):
    risky_words = ["password","otp","bank","verify","login","credit","free","click","win","urgent","account","prize","suspended","hack","threat"]
    suspicious_domains = ["bit.ly","tinyurl","grabify","iplogger","freegift","secure-login","verify-now"]
    fake_news_words = ["breaking","shocking","government hiding","secret cure","they dont want you to know","miracle","exposed","banned","viral"]

    score = 100
    found = []

    for word in risky_words:
        if word in text.lower():
            score -= 15
            found.append(word)

    for domain in suspicious_domains:
        if domain in text.lower():
            score -= 25
            found.append(domain)

    for fake in fake_news_words:
        if fake in text.lower():
            score -= 20
            found.append(fake)

    score = max(0, min(score, 100))

    if score < 40:
        level = "High Risk"
    elif score < 70:
        level = "Medium Risk"
    else:
        level = "Safe"

    return score, level, found

@app.route("/status")
def status():
    status, score = get_target_status()
    return jsonify({"status": status, "safety_score": score})

@app.route("/")
def home():
    return "TrustGuard API Running"

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text","")

    score, level, found = analyze_text(text)

    history.append({
        "text": text,
        "score": score,
        "risk": level
    })

    user_profile["total_scans"] += 1
    if level == "High Risk":
        user_profile["high_risk"] += 1
    elif level == "Medium Risk":
        user_profile["medium_risk"] += 1
    else:
        user_profile["safe"] += 1

    return jsonify({
        "trust_score": score,
        "risk_level": level,
        "flags": found
    })

@app.route("/history")
def get_history():
    return jsonify(history)

@app.route("/profile")
def profile():
    return jsonify(user_profile)

@app.route("/export")
def export():
    report = "TrustGuard Scan Report\n\n"
    for h in history:
        report += f"{h['risk']} ({h['score']}): {h['text']}\n"
    return report

# 🧹 CLEAR HISTORY (NEW)
@app.route("/clear", methods=["POST"])
def clear_history():
    history.clear()
    user_profile["total_scans"] = 0
    user_profile["high_risk"] = 0
    user_profile["medium_risk"] = 0
    user_profile["safe"] = 0
    return jsonify({"status":"cleared"})

if __name__ == "__main__":
    app.run(debug=True)
