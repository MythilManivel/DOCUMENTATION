from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from main import DocumentAnalyzer
import logging
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Use persistent upload directory instead of tempfile
UPLOAD_DIR = Path('data/uploads')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'your-secret-key-here'  # Change this in production

# Store processed document IDs
processed_documents = {}  # Maps filepath to document_id
processing_status = {}    # Maps filepath to processing status

# Initialize the document analyzer
try:
    analyzer = DocumentAnalyzer()
    logger.info("DocumentAnalyzer initialized successfully")
except Exception as e:
    logger.error(f"Error initializing DocumentAnalyzer: {e}")
    analyzer = None

@app.route('/')
def index():
    return render_template('index.html')

def process_document_background(filepath, document_id):
    """Process document in background thread"""
    try:
        logger.info(f"Background: Starting document processing for {filepath}")
        processing_status[filepath] = {'status': 'processing', 'progress': 10}
        
        result = analyzer.process_document(Path(filepath))
        
        if result.get("success"):
            processing_status[filepath] = {'status': 'completed', 'progress': 100}
            processed_documents[str(filepath)] = document_id
            logger.info(f"Background: Document processed successfully: {document_id}")
        else:
            error = result.get('error', 'Unknown error')
            processing_status[filepath] = {'status': 'failed', 'error': error}
            logger.error(f"Background: Document processing failed: {error}")
    except Exception as e:
        error_msg = str(e)
        processing_status[filepath] = {'status': 'failed', 'error': error_msg}
        logger.error(f"Background: Exception during processing: {error_msg}", exc_info=True)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running"""
    try:
        status = {
            'status': 'healthy',
            'analyzer_initialized': analyzer is not None,
            'upload_dir_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
            'processed_documents_count': len(processed_documents)
        }
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/processing-status/<filepath>', methods=['GET'])
def get_processing_status(filepath):
    """Check the processing status of an uploaded document"""
    try:
        # Decode the filepath if it's URL encoded
        from urllib.parse import unquote
        filepath = unquote(filepath)
        
        status = processing_status.get(filepath)
        if status:
            return jsonify(status), 200
        else:
            # If not found in processing_status, check if already processed
            if filepath in processed_documents:
                return jsonify({'status': 'completed', 'progress': 100}), 200
            else:
                return jsonify({'status': 'unknown', 'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error checking processing status: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload and queue for processing."""
    import time
    start_time = time.time()
    
    try:
        if 'file' not in request.files:
            logger.warning("Upload attempt without file part")
            return jsonify({'success': False, 'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("Upload attempt with empty filename")
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        if not file.filename.endswith('.pdf'):
            logger.warning(f"Upload attempt with non-PDF file: {file.filename}")
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload a PDF file.'}), 400
        
        # Validate analyzer is initialized
        if analyzer is None:
            logger.error("DocumentAnalyzer not initialized")
            return jsonify({'success': False, 'error': 'Server is not properly configured. Please contact support.'}), 500
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(filepath)
            logger.info(f"File saved: {filename}")
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return jsonify({'success': False, 'error': 'Failed to save file. Please try again.'}), 500
        
        # Validate file exists before processing
        if not os.path.exists(filepath):
            logger.error(f"File not found after save: {filepath}")
            return jsonify({'success': False, 'error': 'File was not saved correctly. Please try again.'}), 500
        
        # Generate document ID
        document_id = os.path.splitext(filename)[0] + '_' + str(int(time.time()))
        
        # Start background processing thread
        processing_status[filepath] = {'status': 'queued', 'progress': 0}
        processing_thread = threading.Thread(
            target=process_document_background,
            args=(filepath, document_id),
            daemon=True
        )
        processing_thread.start()
        
        # Return immediately with document ID
        response_data = {
            'success': True,
            'filename': str(filename),
            'filepath': str(filepath),
            'document_id': document_id,
            'message': 'PDF uploaded successfully! Processing in background. You can now view summary or ask questions.'
        }
        
        logger.info(f"Upload response sent. Processing will continue in background. Document ID: {document_id}")
        return jsonify(response_data), 200
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error in upload handler: {error_msg}", exc_info=True)
        return jsonify({'success': False, 'error': 'An unexpected error occurred. Please try again.'}), 500
        return jsonify({'success': False, 'error': 'An unexpected error occurred. Please try again.'}), 500


@app.route('/summarize', methods=['POST'])
def summarize():
    """Generate summary for uploaded PDF."""
    try:
        data = request.get_json()
        filepath = data.get('filepath')
        
        if not filepath or not os.path.exists(filepath):
            logger.warning("Summarize requested for non-existent file")
            return jsonify({'success': False, 'error': 'File not found. Please upload again.'}), 400
        
        if analyzer is None:
            logger.error("DocumentAnalyzer not initialized")
            return jsonify({'success': False, 'error': 'Server is not properly configured.'}), 500
        
        # Check if document was already processed
        document_id = processed_documents.get(str(filepath))
        
        if document_id:
            # Document already processed, just get the summary
            logger.info(f"Document already processed, generating summary for: {filepath}")
            doc = analyzer.document_store.get_document(document_id)
            if doc:
                summary = analyzer.summarizer.generate_structured_summary(doc["full_text"])
            else:
                # Fallback: reprocess
                logger.warning("Document not found in store, reprocessing...")
                result = analyzer.process_document(Path(filepath))
                if not result.get("success"):
                    return jsonify({'success': False, 'error': 'Failed to process document'}), 400
                summary = result["summary"]
                document_id = result.get("document_id")
        else:
            # Process document if not already processed
            logger.info(f"Processing document for summary: {filepath}")
            result = analyzer.process_document(Path(filepath))
            
            if not result.get("success"):
                error_msg = result.get('error', 'Failed to process document')
                logger.error(f"Summarization failed: {error_msg}")
                return jsonify({'success': False, 'error': str(error_msg)}), 400
            
            summary = result["summary"]
            document_id = result.get("document_id")
            processed_documents[str(filepath)] = document_id
        
        try:
            formatted_summary = analyzer.summarizer.format_summary_output(summary)
            if not isinstance(formatted_summary, str):
                formatted_summary = str(formatted_summary)
            logger.info(f"Summary generated successfully")
        except Exception as e:
            logger.error(f"Error formatting summary: {e}", exc_info=True)
            formatted_summary = f"Summary generated but formatting failed: {str(e)}"
        
        response_data = {
            'success': True,
            'summary': str(formatted_summary),
            'document_id': str(document_id) if document_id else None
        }
        
        logger.info(f"Sending summary response with {len(response_data['summary'])} chars")
        return jsonify(response_data), 200
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Exception during summarization: {error_msg}", exc_info=True)
        return jsonify({'success': False, 'error': f'Error: {error_msg}'}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle question answering on uploaded document."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        filepath = data.get('filepath')  # Get filepath from request
        
        if not question:
            logger.warning("Question endpoint called with empty question")
            return jsonify({'success': False, 'error': 'No question provided'}), 400
        
        if analyzer is None:
            logger.error("DocumentAnalyzer not initialized")
            return jsonify({'success': False, 'error': 'Server is not properly configured.'}), 500
        
        # Get document ID from processed documents
        document_id = None
        if filepath:
            document_id = processed_documents.get(str(filepath))
        
        # If no document_id found, try to use current_document_id
        if not document_id:
            document_id = analyzer.current_document_id
        
        if not document_id:
            logger.warning("No document loaded for Q&A")
            return jsonify({
                'success': False, 
                'error': 'No document loaded. Please upload and process a document first.'
            }), 400
        
        # Set the active document
        analyzer.current_document_id = document_id
        analyzer.interactive_chatbot.set_active_document(document_id)
        
        logger.info(f"Processing question: {question} (document_id: {document_id})")
        answer = analyzer.ask_question(question)
        
        # Check if answer has error or if answer is empty/invalid
        if 'error' in answer:
            error_msg = answer.get('error', 'Unknown error occurred')
            logger.error(f"Question processing error: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Check if we got a valid answer
        answer_text = answer.get('answer', '')
        if not answer_text or answer_text.strip() == '':
            logger.warning("Empty answer received")
            return jsonify({
                'success': False,
                'error': 'No answer could be generated. Please try rephrasing your question.'
            }), 400
        
        confidence = answer.get('confidence', 0.0)
        logger.info(f"Question processed successfully (confidence: {confidence:.2f})")
        
        return jsonify({
            'success': True,
            'answer': answer_text,
            'confidence': confidence
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Exception during question processing: {error_msg}", exc_info=True)
        return jsonify({'success': False, 'error': f'Error processing question: {error_msg}'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create a simple HTML template
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document Analysis System</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        </head>
        <body class="bg-gray-100 min-h-screen">
            <div class="container mx-auto px-4 py-8">
                <h1 class="text-3xl font-bold text-center mb-8">Document Analysis System</h1>
                
                <!-- Upload Section -->
                <div class="bg-white rounded-lg shadow-md p-6 mb-8">
                    <h2 class="text-xl font-semibold mb-4">Upload Document</h2>
                    <div class="flex items-center justify-center w-full">
                        <label for="file-upload" class="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                            <div class="flex flex-col items-center justify-center pt-5 pb-6">
                                <svg class="w-8 h-8 mb-4 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                                </svg>
                                <p class="mb-2 text-sm text-gray-500"><span class="font-semibold">Click to upload</span> or drag and drop</p>
                                <p class="text-xs text-gray-500">PDF (MAX. 16MB)</p>
                            </div>
                            <input id="file-upload" type="file" class="hidden" accept=".pdf" />
                        </label>
                    </div>
                <!-- Upload Progress -->
                    <div id="upload-progress" class="mt-4 hidden">
                        <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                            <div id="progress-bar" class="bg-blue-600 h-2.5 rounded-full transition-all duration-300" style="width: 0%"></div>
                        </div>
                        <p id="progress-text" class="text-sm text-gray-600 mt-2 font-medium">Uploading: 0%</p>
                    </div>
                    
                    <!-- Action Buttons (shown after successful upload) -->
                    <div id="action-buttons" class="mt-6 hidden flex gap-4">
                        <button id="summarize-btn" class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors font-semibold flex items-center gap-2">
                            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M5 3a2 2 0 00-2 2v6h6V5a2 2 0 00-2-2H5z"></path>
                                <path d="M15 3a2 2 0 00-2 2v6h6V5a2 2 0 00-2-2h-2z"></path>
                                <path d="M3 13a2 2 0 012-2h2v6H5a2 2 0 01-2-2v-2z"></path>
                                <path d="M13 11h2a2 2 0 012 2v2a2 2 0 01-2 2h-2v-6z"></path>
                            </svg>
                            Summarize
                        </button>
                        <button id="qa-btn" class="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-colors font-semibold flex items-center gap-2">
                            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2zm-11-1a1 1 0 11-2 0 1 1 0 012 0z" clip-rule="evenodd"></path>
                            </svg>
                            Ask Questions
                        </button>
                    </div>
                </div>
                
                <!-- Summary Section -->
                <div id="summary-section" class="bg-white rounded-lg shadow-md p-6 mb-8 hidden">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-xl font-semibold">Document Summary</h2>
                        <button id="close-summary-btn" class="text-gray-500 hover:text-gray-700 text-xl">✕</button>
                    </div>
                    <!-- Error Alert -->
                    <div id="summary-error" class="hidden mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-start gap-3">
                        <svg class="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                        </svg>
                        <div id="summary-error-text" class="text-sm"></div>
                    </div>
                    <!-- Summary Content -->
                    <div id="summary-content" class="prose max-w-none hidden text-gray-700 space-y-4"></div>
                    <!-- Loading State -->
                    <div id="summary-loading" class="hidden text-center py-8">
                        <div class="inline-block">
                            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                        </div>
                        <p class="text-gray-600 mt-4">Generating summary...</p>
                    </div>
                </div>
                
                <!-- Q&A Section -->
                <div id="qa-section" class="bg-white rounded-lg shadow-md p-6 hidden">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-xl font-semibold">Ask Questions</h2>
                        <button id="close-qa-btn" class="text-gray-500 hover:text-gray-700 text-xl">✕</button>
                    </div>
                    
                    <div class="flex gap-2 mb-6">
                        <input type="text" id="question-input" placeholder="Ask something about the document..." class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500">
                        <button id="ask-button" class="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-colors font-semibold">Ask</button>
                    </div>
                    
                    <!-- Q&A Error Alert -->
                    <div id="qa-error" class="hidden mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-start gap-3">
                        <svg class="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                        </svg>
                        <div id="qa-error-text" class="text-sm"></div>
                    </div>
                    
                    <!-- Answer Container -->
                    <div id="answer-container" class="hidden mt-6 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                        <div class="font-medium text-purple-900">Answer:</div>
                        <div id="answer-text" class="mt-2 text-gray-700"></div>
                        <div id="confidence" class="text-sm text-purple-700 mt-3 font-medium"></div>
                    </div>
                    
                    <!-- Loading State -->
                    <div id="qa-loading" class="hidden text-center py-8">
                        <div class="inline-block">
                            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                        </div>
                        <p class="text-gray-600 mt-4">Processing your question...</p>
                    </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Logger utility for debugging
                const Logger = {
                    log: function(message, data = null) {
                        console.log(`[App] ${message}`, data || '');
                    },
                    error: function(message, error = null) {
                        console.error(`[Error] ${message}`, error || '');
                    },
                    warn: function(message, data = null) {
                        console.warn(`[Warning] ${message}`, data || '');
                    }
                };
                
                document.addEventListener('DOMContentLoaded', function() {
                    // DOM Elements
                    const fileUpload = document.getElementById('file-upload');
                    const uploadProgress = document.getElementById('upload-progress');
                    const progressBar = document.getElementById('progress-bar');
                    const progressText = document.getElementById('progress-text');
                    
                    const actionButtons = document.getElementById('action-buttons');
                    const summarizeBtn = document.getElementById('summarize-btn');
                    const qaBtn = document.getElementById('qa-btn');
                    
                    const summarySection = document.getElementById('summary-section');
                    const summaryContent = document.getElementById('summary-content');
                    const summaryError = document.getElementById('summary-error');
                    const summaryErrorText = document.getElementById('summary-error-text');
                    const summaryLoading = document.getElementById('summary-loading');
                    const closeSummaryBtn = document.getElementById('close-summary-btn');
                    
                    const qaSection = document.getElementById('qa-section');
                    const questionInput = document.getElementById('question-input');
                    const askButton = document.getElementById('ask-button');
                    const qaError = document.getElementById('qa-error');
                    const qaErrorText = document.getElementById('qa-error-text');
                    const qaLoading = document.getElementById('qa-loading');
                    const closeQABtn = document.getElementById('close-qa-btn');
                    const answerContainer = document.getElementById('answer-container');
                    const answerText = document.getElementById('answer-text');
                    const confidenceText = document.getElementById('confidence');
                    
                    let currentFilepath = null;
                    let currentDocumentId = null;
                    
                    // Helper functions
                    function showSummaryError(errorMessage) {
                        Logger.error('Summary error', errorMessage);
                        summaryErrorText.textContent = errorMessage;
                        summaryError.classList.remove('hidden');
                        summaryContent.classList.add('hidden');
                        summaryLoading.classList.add('hidden');
                        summarySection.classList.remove('hidden');
                    }
                    
                    function showSummarySuccess(summaryText) {
                        Logger.log('Summary displayed successfully');
                        summaryContent.innerHTML = summaryText.replace(/\n/g, '<br>');
                        summaryContent.classList.remove('hidden');
                        summaryError.classList.add('hidden');
                        summaryLoading.classList.add('hidden');
                        summarySection.classList.remove('hidden');
                    }
                    
                    function showQAError(errorMessage) {
                        Logger.error('Q&A error', errorMessage);
                        qaErrorText.textContent = errorMessage;
                        qaError.classList.remove('hidden');
                        answerContainer.classList.add('hidden');
                        qaLoading.classList.add('hidden');
                    }
                    
                    function resetUI() {
                        summarySection.classList.add('hidden');
                        qaSection.classList.add('hidden');
                        actionButtons.classList.add('hidden');
                        uploadProgress.classList.add('hidden');
                    }
                    
                    // File Upload
                    fileUpload.addEventListener('change', function(e) {
                        const file = e.target.files[0];
                        if (!file) {
                            Logger.warn('File selection cancelled');
                            return;
                        }
                        
                        Logger.log('File selected', { name: file.name, size: file.size });
                        resetUI();
                        
                        uploadProgress.classList.remove('hidden');
                        progressBar.style.width = '0%';
                        progressText.textContent = 'Uploading: 0%';
                        
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        const xhr = new XMLHttpRequest();
                        xhr.open('POST', '/upload', true);
                        
                        xhr.upload.onprogress = function(e) {
                            if (e.lengthComputable) {
                                const percentComplete = (e.loaded / e.total) * 100;
                                progressBar.style.width = percentComplete + '%';
                                progressText.textContent = `Uploading: ${Math.round(percentComplete)}%`;
                            }
                        };
                        
                        xhr.onload = function() {
                            Logger.log('Upload completed', { status: xhr.status });
                            
                            try {
                                const response = JSON.parse(xhr.responseText);
                                
                                if (xhr.status === 200 && response.success) {
                                    progressText.textContent = 'Upload successful!';
                                    currentFilepath = response.filepath;
                                    Logger.log('File ready for processing', { filepath: response.filepath });
                                    
                                    // Show action buttons
                                    setTimeout(() => {
                                        actionButtons.classList.remove('hidden');
                                    }, 500);
                                } else {
                                    const errorMsg = response.error || 'Upload failed';
                                    progressText.textContent = 'Upload failed';
                                    Logger.error('Upload error', errorMsg);
                                    alert('Error: ' + errorMsg);
                                }
                            } catch (parseError) {
                                Logger.error('Failed to parse response', parseError);
                                progressText.textContent = 'Upload failed';
                                alert('Server error. Please try again.');
                            }
                        };
                        
                        xhr.onerror = function() {
                            Logger.error('Upload request failed');
                            uploadProgress.classList.add('hidden');
                            alert('Network error. Please check your connection.');
                        };
                        
                        xhr.send(formData);
                    });
                    
                    // Summarize Button
                    summarizeBtn.addEventListener('click', function() {
                        if (!currentFilepath) {
                            Logger.warn('No file loaded');
                            alert('Please upload a PDF first');
                            return;
                        }
                        
                        Logger.log('Summarize button clicked');
                        resetUI();
                        summarySection.classList.remove('hidden');
                        summaryLoading.classList.remove('hidden');
                        summaryError.classList.add('hidden');
                        summaryContent.classList.add('hidden');
                        summarizeBtn.disabled = true;
                        qaBtn.disabled = true;
                        
                        fetch('/summarize', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ filepath: currentFilepath })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                Logger.log('Summary received');
                                currentDocumentId = data.document_id;
                                showSummarySuccess(data.summary);
                            } else {
                                const errorMsg = data.error || 'Failed to generate summary';
                                showSummaryError(errorMsg);
                            }
                        })
                        .catch(error => {
                            Logger.error('Summarize request failed', error);
                            showSummaryError('Network error. Please try again.');
                        })
                        .finally(() => {
                            summarizeBtn.disabled = false;
                            qaBtn.disabled = false;
                        });
                    });
                    
                    // Q&A Button
                    qaBtn.addEventListener('click', function() {
                        if (!currentFilepath) {
                            Logger.warn('No file loaded');
                            alert('Please upload a PDF first');
                            return;
                        }
                        
                        Logger.log('Q&A button clicked');
                        resetUI();
                        qaSection.classList.remove('hidden');
                        questionInput.focus();
                    });
                    
                    // Ask Question
                    function askQuestion() {
                        const question = questionInput.value.trim();
                        if (!question) {
                            Logger.warn('Empty question');
                            return;
                        }
                        
                        Logger.log('Asking question', { question: question.substring(0, 50) + '...' });
                        
                        askButton.disabled = true;
                        answerContainer.classList.add('hidden');
                        qaError.classList.add('hidden');
                        qaLoading.classList.remove('hidden');
                        
                        fetch('/ask', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ 
                                question: question,
                                filepath: currentFilepath 
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                Logger.log('Answer received');
                                answerText.textContent = data.answer;
                                confidenceText.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;
                                answerContainer.classList.remove('hidden');
                                questionInput.value = '';
                            } else {
                                const errorMsg = data.error || 'Failed to get answer';
                                showQAError(errorMsg);
                            }
                        })
                        .catch(error => {
                            Logger.error('Question request failed', error);
                            showQAError('Network error. Please try again.');
                        })
                        .finally(() => {
                            askButton.disabled = false;
                            qaLoading.classList.add('hidden');
                        });
                    }
                    
                    // Close Buttons
                    closeSummaryBtn.addEventListener('click', () => {
                        summarySection.classList.add('hidden');
                        actionButtons.classList.remove('hidden');
                    });
                    
                    closeQABtn.addEventListener('click', () => {
                        qaSection.classList.add('hidden');
                        actionButtons.classList.remove('hidden');
                    });
                    
                    // Event Listeners
                    askButton.addEventListener('click', askQuestion);
                    questionInput.addEventListener('keypress', function(e) {
                        if (e.key === 'Enter' && !askButton.disabled) {
                            askQuestion();
                        }
                    });
                    
                    Logger.log('App initialized successfully');
                });
            </script>
        </body>
        </html>
        """)
    
    # Run the app
    app.run(debug=False, port=5000)
