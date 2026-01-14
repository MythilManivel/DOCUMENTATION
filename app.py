from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Temporary in-memory storage
stored_data = {
    "text": None
}

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "File key not found!"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No file selected!"}), 400

    try:
        text = file.read().decode("utf-8").strip()
    except UnicodeDecodeError:
        return jsonify({"message": "Only UTF-8 text files are supported!"}), 400

    stored_data["text"] = text

    return jsonify({
        "message": "File uploaded successfully!",
        "length": len(text)
    })


@app.route("/summary", methods=["GET"])
def summary():
    text = stored_data.get("text")

    if not text:
        return jsonify({"summary": "No document uploaded yet!"}), 400

    # Simple summary logic
    summary_text = text[:200]
    if len(text) > 200:
        summary_text += "..."

    return jsonify({"summary": summary_text})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)

    if not data or "question" not in data:
        return jsonify({"answer": "Please provide a question!"}), 400

    question = data["question"].lower().strip()
    text = stored_data.get("text")

    if not text:
        return jsonify({"answer": "Upload a document first!"}), 400

    if question in text.lower():
        answer = "Yes, this information is present in the document."
    else:
        answer = "Sorry, I couldn’t find this in the document."

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
