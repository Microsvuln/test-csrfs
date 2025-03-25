import random
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for session management

class UserSession:
    def __init__(self):
        self.store = {}

    def set_value(self, key, value):
        self.store[key] = value

    def get_value(self, key):
        return self.store.get(key)

class MessageHandler:
    messages = {
        "csrf-null-referer.success": "CSRF validation passed with null referer",
        "csrf-other-referer.success": "CSRF validation passed with different referer"
    }

    @staticmethod
    def get_message(key):
        return MessageHandler.messages.get(key, "Unknown message")

session_manager = UserSession()
message_handler = MessageHandler()

@app.route("/csrf/validate", methods=["POST"])
def process_request():
    response = {}

    request_host = request.headers.get("Host", "NULL")
    referer_header = request.headers.get("Referer", "NULL")
    referer_segments = referer_header.split("/")
    
    if referer_header == "NULL":
        if request.form.get("csrf") == "true":
            session_manager.set_value("csrf-validation-success", random.randint(0, 65535))
            response["success"] = True
            response["message"] = message_handler.get_message("csrf-null-referer.success")
            response["flag"] = session_manager.get_value("csrf-validation-success")
        else:
            session_manager.set_value("csrf-validation-success", random.randint(0, 65535))
            response["success"] = True
            response["message"] = message_handler.get_message("csrf-other-referer.success")
            response["flag"] = session_manager.get_value("csrf-validation-success")
    elif referer_segments[2] == request_host:
        response["success"] = False
        response["message"] = "Request originates from the expected host"
        response["flag"] = None
    else:
        session_manager.set_value("csrf-validation-success", random.randint(0, 65535))
        response["success"] = True
        response["message"] = message_handler.get_message("csrf-other-referer.success")
        response["flag"] = session_manager.get_value("csrf-validation-success")

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)