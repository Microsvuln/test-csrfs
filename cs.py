from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps

app = Flask(__name__)

# Sample CSRF token and review data
CSRF_TOKEN = "2aa14227b9a13d0bede0388a7fba9aa9"
user_review_map = {}
default_reviews = [
    {"user": "user1", "date": datetime.now().strftime("%Y-%m-%d, %H:%M:%S"), "text": "Security is questionable", "rating": 0},
    {"user": "user2", "date": datetime.now().strftime("%Y-%m-%d, %H:%M:%S"), "text": "Decent functionality", "rating": 2},
    {"user": "guest", "date": datetime.now().strftime("%Y-%m-%d, %H:%M:%S"), "text": "Great app!", "rating": 5},
    {"user": "guest", "date": datetime.now().strftime("%Y-%m-%d, %H:%M:%S"), "text": "I never wrote this review! Can you manipulate this too?", "rating": 1},
]

# Mock CurrentUser decorator
def current_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        username = request.args.get("username", "guest")  # Mock current user from query parameter
        return func(username=username, *args, **kwargs)
    return wrapper

@app.route("/reviews", methods=["GET"])
@current_user
def get_reviews(username):
    all_reviews = []
    user_specific_reviews = user_review_map.get(username, [])
    if user_specific_reviews:
        all_reviews.extend(user_specific_reviews)
    all_reviews.extend(default_reviews)
    return jsonify(all_reviews)

@app.route("/reviews", methods=["POST"])
@current_user
def add_review(username):
    review_text = request.form.get("reviewText")
    rating = int(request.form.get("rating"))
    csrf_validation = request.form.get("csrfValidation")
    host_header = request.headers.get("Host", "NULL")
    referer_header = request.headers.get("Referer", "NULL")
    referer_parts = referer_header.split("/") if referer_header != "NULL" else []

    new_review = {
        "user": username,
        "date": datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
        "text": review_text,
        "rating": rating
    }

    user_reviews = user_review_map.get(username, [])
    user_reviews.append(new_review)
    user_review_map[username] = user_reviews

    if not csrf_validation or csrf_validation != CSRF_TOKEN:
        return jsonify({"status": "failure", "message": "missing-csrf-token"}), 400

    if referer_header != "NULL" and len(referer_parts) > 2 and referer_parts[2] == host_header:
        return jsonify({"status": "failure", "message": "invalid-referer"}), 400

    return jsonify({"status": "success", "message": "review-submitted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
