from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

stored_data = {}  # temporary in-memory storage

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")

    if not file:
        return jsonify({"message": "No file uploaded!"}), 400

    try:
        text = file.read().decode("utf-8")
    except Exception:
        return jsonify({"message": "Invalid file format!"}), 400

    stored_data["text"] = text.strip()

    return jsonify({"message": "File uploaded successfully!"})


@app.route("/summary", methods=["GET"])
def summary():
    text = stored_data.get("text")

    if not text:
        return jsonify({"summary": "No document uploaded yet!"})

    # Simple summary logic
    summary_text = text[:200] + "..." if len(text) > 200 else text

    return jsonify({"summary": summary_text})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").lower()

    text = stored_data.get("text")

    if not text:
        return jsonify({"answer": "Upload a document first!"})

    if question and question in text.lower():
        answer = "Yes, this information is present in the document."
    else:
        answer = "Sorry, I couldn’t find this in the document."

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
