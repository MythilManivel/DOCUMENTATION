from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from main import DocumentAnalyzer
import logging
import threading
import time

# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Flask App Setup
# --------------------------------------------------
app = Flask(__name__)

UPLOAD_DIR = Path('data/uploads')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.secret_key = 'your-secret-key-here'  # change in production

# --------------------------------------------------
# Global Stores
# --------------------------------------------------
processed_documents = {}   # filepath (str) -> document_id
processing_status = {}     # filepath (str) -> status

# --------------------------------------------------
# Initialize Analyzer
# --------------------------------------------------
try:
    analyzer = DocumentAnalyzer()
    logger.info("DocumentAnalyzer initialized successfully")
except Exception as e:
    logger.error(f"Error initializing DocumentAnalyzer: {e}")
    analyzer = None

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


def process_document_background(filepath, document_id):
    """Process document in background thread"""
    filepath = str(filepath)
    try:
        logger.info(f"Background processing started: {filepath}")
        processing_status[filepath] = {'status': 'processing', 'progress': 10}

        result = analyzer.process_document(Path(filepath))

        if result.get("success"):
            processing_status[filepath] = {'status': 'completed', 'progress': 100}
            processed_documents[filepath] = document_id
            logger.info(f"Document processed successfully: {document_id}")
        else:
            error = result.get('error', 'Unknown error')
            processing_status[filepath] = {'status': 'failed', 'error': error}
            logger.error(f"Processing failed: {error}")

    except Exception as e:
        processing_status[filepath] = {'status': 'failed', 'error': str(e)}
        logger.error("Exception during background processing", exc_info=True)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'analyzer_initialized': analyzer is not None,
        'upload_dir_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
        'processed_documents_count': len(processed_documents)
    }), 200


@app.route('/processing-status/<filepath>', methods=['GET'])
def get_processing_status(filepath):
    from urllib.parse import unquote
    filepath = unquote(filepath)

    status = processing_status.get(filepath)
    if status:
        return jsonify(status), 200

    if filepath in processed_documents:
        return jsonify({'status': 'completed', 'progress': 100}), 200

    return jsonify({'status': 'unknown', 'error': 'File not found'}), 404


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files allowed'}), 400

        if analyzer is None:
            return jsonify({'success': False, 'error': 'Analyzer not initialized'}), 500

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(filepath)

        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File save failed'}), 500

        document_id = f"{os.path.splitext(filename)[0]}_{int(time.time())}"

        processing_status[str(filepath)] = {'status': 'queued', 'progress': 0}

        thread = threading.Thread(
            target=process_document_background,
            args=(filepath, document_id),
            daemon=True
        )
        thread.start()

        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath,
            'document_id': document_id,
            'message': 'PDF uploaded successfully. Processing started.'
        }), 200

    except Exception:
        logger.error("Upload handler error", exc_info=True)
        return jsonify({'success': False, 'error': 'Unexpected server error'}), 500


@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        filepath = data.get('filepath')

        if not filepath or not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 400

        document_id = processed_documents.get(filepath)

        if not document_id:
            result = analyzer.process_document(Path(filepath))
            if not result.get("success"):
                return jsonify({'success': False, 'error': 'Processing failed'}), 400

            document_id = result.get("document_id")
            processed_documents[filepath] = document_id
            summary = result["summary"]
        else:
            doc = analyzer.document_store.get_document(document_id)
            summary = analyzer.summarizer.generate_structured_summary(doc["full_text"])

        formatted_summary = analyzer.summarizer.format_summary_output(summary)

        return jsonify({
            'success': True,
            'summary': str(formatted_summary),
            'document_id': document_id
        }), 200

    except Exception:
        logger.error("Summarization error", exc_info=True)
        return jsonify({'success': False, 'error': 'Summarization failed'}), 500


@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        filepath = data.get('filepath')

        if not question:
            return jsonify({'success': False, 'error': 'Question is empty'}), 400

        document_id = processed_documents.get(filepath) or analyzer.current_document_id
        if not document_id:
            return jsonify({'success': False, 'error': 'No document loaded'}), 400

        analyzer.current_document_id = document_id
        analyzer.interactive_chatbot.set_active_document(document_id)

        answer = analyzer.ask_question(question)

        if 'error' in answer:
            return jsonify({'success': False, 'error': answer['error']}), 400

        return jsonify({
            'success': True,
            'answer': answer.get('answer', ''),
            'confidence': answer.get('confidence', 0.0)
        }), 200

    except Exception:
        logger.error("Q&A error", exc_info=True)
        return jsonify({'success': False, 'error': 'Question processing failed'}), 500


# --------------------------------------------------
# Run App
# --------------------------------------------------
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(debug=False, port=5000)
