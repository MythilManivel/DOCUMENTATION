from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

stored_data = {}  # temporary storage

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]

    # convert file content to text
    text = file.read().decode("utf-8")

    # Save text (so summary endpoint can read it)
    global stored_data
    stored_data["text"] = text

    return jsonify({"message": "File uploaded successfully!"})

@app.route("/summary", methods=["GET"])
def summary():
    if "text" not in stored_data:
        return jsonify({"summary": "No document uploaded yet!"})

    text = stored_data["text"]

    # Create simple summary
    summary_text = text[:150] + "..." if len(text) > 150 else text

    return jsonify({"summary": summary_text})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data["question"]

    if "text" not in stored_data:
        return jsonify({"answer": "Upload a document first!"})

    text = stored_data["text"]

    # Simple Q&A (keyword search)
    if question.lower() in text.lower():
        return jsonify({"answer": "Yes, this information exists in the document."})
    else:
        return jsonify({"answer": "Not found in the document."})

if __name__ == '__main__':
    app.run(debug=True)
