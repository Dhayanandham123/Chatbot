from flask import Flask, render_template, request, jsonify
import json
import os
import webbrowser

app = Flask(__name__)

# Load courses
with open("courses.json", "r") as f:
    courses = json.load(f)

# Load or create progress file
progress_file = "progress.json"
if os.path.exists(progress_file):
    with open(progress_file, "r") as f:
        progress = json.load(f)
else:
    progress = {}

# Recommender logic
def recommend_courses(user_input):
    words = user_input.lower().split()
    recommended = []
    for course in courses:
        if any(word in course["skills"] + course["career"] for word in words):
            recommended.append(course)
    return recommended

# Save progress
def save_progress(title):
    progress[title] = "Completed"
    with open(progress_file, "w") as f:
        json.dump(progress, f)

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json["message"]

    if user_msg.lower().startswith("done:"):
        course_name = user_msg[5:].strip()
        save_progress(course_name)
        return jsonify({"response": f"✅ '{course_name}' marked as completed!"})

    elif user_msg.lower() == "progress":
        if not progress:
            return jsonify({"response": "You haven't completed any courses yet."})
        status = "\n".join([f"- {title}: {state}" for title, state in progress.items()])
        return jsonify({"response": f"📊 Your completed courses:\n{status}"})

    else:
        recs = recommend_courses(user_msg)
        if not recs:
            return jsonify({"response": "❌ Sorry, I couldn't find any matching courses."})
        msg = "📚 Recommended courses:\n"
        for c in recs:
            msg += f"\n🔹 {c['title']}\nSkills: {', '.join(c['skills'])}\nCareers: {', '.join(c['career'])}\n"
        return jsonify({"response": msg})

# Run the app and open browser
if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=True)
