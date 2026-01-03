# API Documentation - Updated Endpoints

## Response Format

All endpoints now return consistent JSON response format:

```json
{
  "success": true|false,
  "error": "error message if success=false",
  ...additional fields...
}
```

---

## POST `/upload`

Uploads and processes a PDF file.

### Request
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Required Files**: `file` (PDF only)
- **Max Size**: 16MB

```javascript
const formData = new FormData();
formData.append('file', pdfFile);
fetch('/upload', {
  method: 'POST',
  body: formData
})
```

### Success Response (200 OK)
```json
{
  "success": true,
  "filename": "document.pdf",
  "summary": "Formatted summary text with newlines...",
  "document_id": "abc123def456"
}
```

### Error Responses

**400 - No File Part**
```json
{
  "success": false,
  "error": "No file part"
}
```

**400 - No Selected File**
```json
{
  "success": false,
  "error": "No selected file"
}
```

**400 - Invalid File Type**
```json
{
  "success": false,
  "error": "Invalid file type. Please upload a PDF file."
}
```

**400 - Document Processing Failed**
```json
{
  "success": false,
  "error": "Description of what went wrong during processing"
}
```

**500 - Server Error**
```json
{
  "success": false,
  "error": "Error processing document: [specific error]"
}
```

### Status Codes
- `200`: File uploaded and processed successfully
- `400`: Client error (invalid file, missing file, processing failed)
- `500`: Server error (analyzer not initialized, save failure, unexpected error)

### Logging
Server logs all upload attempts:
```
2025-12-30 14:25:30,123 - INFO - File saved: document.pdf
2025-12-30 14:25:31,456 - INFO - Processing document: document.pdf
2025-12-30 14:25:35,789 - INFO - Document processed successfully: document.pdf
```

---

## POST `/ask`

Asks a question about the uploaded document.

### Request
- **Method**: POST
- **Content-Type**: application/json
- **Required Body**: JSON with `question` field

```javascript
fetch('/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question: "What is the main topic of this document?"
  })
})
```

### Success Response (200 OK)
```json
{
  "success": true,
  "answer": "The main topic is...",
  "confidence": 0.85
}
```

### Error Responses

**400 - Empty Question**
```json
{
  "success": false,
  "error": "No question provided"
}
```

**500 - Server Error**
```json
{
  "success": false,
  "error": "Error processing question: [specific error]"
}
```

**500 - Analyzer Not Initialized**
```json
{
  "success": false,
  "error": "Server is not properly configured."
}
```

### Status Codes
- `200`: Question processed successfully
- `400`: Client error (empty question)
- `500`: Server error (analyzer not initialized, processing failed)

### Logging
Server logs all questions:
```
2025-12-30 14:26:01,456 - INFO - Processing question: What is this document about?
2025-12-30 14:26:02,789 - INFO - Question processed successfully
```

---

## GET `/`

Returns the HTML interface.

### Request
- **Method**: GET
- **Content-Type**: text/html

### Response
- `200`: Returns rendered index.html template

---

## Error Handling

### Client-Side
All endpoints should check the `success` field:

```javascript
fetch('/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    // Handle success
    console.log("Upload successful:", data.filename);
  } else {
    // Handle error
    console.error("Upload failed:", data.error);
  }
})
.catch(error => {
  // Network error
  console.error("Network error:", error);
})
```

### Server-Side
All errors are logged with context:

```
[WARNING] Upload attempt without file part
[ERROR] Document processing failed for document.pdf: Extraction failed
[ERROR] Exception during question processing: NoneType error (exc_info=True)
```

---

## Response Headers

### Content-Type
- `/upload`: `application/json`
- `/ask`: `application/json`
- `/`: `text/html; charset=utf-8`

### CORS
Currently no CORS headers. Add if needed:
```python
from flask_cors import CORS
CORS(app)
```

---

## Rate Limiting

Not currently implemented. Consider adding for production:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")
def upload_file():
    ...
```

---

## Authentication

Not currently implemented. Consider adding for production:
```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # Verify logic here
    pass

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    ...
```

---

## Migration from Old API

### Old Response Format
```json
{"error": "message"}  // on error only
{"success": true, "summary": "..."}  // on success
```

### New Response Format
```json
{
  "success": false,
  "error": "message"
}
// AND
{
  "success": true,
  "summary": "...",
  "filename": "...",
  "document_id": "..."
}
```

### Client Updates Required
1. Check `success` field instead of presence of `error`
2. Always expect consistent JSON structure
3. Use `response.error` instead of `response.error` or thrown error
4. Handle 400 status codes as well as 500

### Example Update
```javascript
// OLD
if (response.error) {
  alert('Error: ' + response.error);
}

// NEW
if (!response.success) {
  showError(response.error);
}
```

---

## Testing with cURL

### Upload PDF
```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:5000/upload
```

### Ask Question
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this?"}' \
  http://localhost:5000/ask
```

---

## WebSocket Support

Not currently implemented. For real-time progress, consider:
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('upload')
def handle_upload(data):
    # Emit progress events
    emit('progress', {'percent': 25})
    emit('progress', {'percent': 50})
    emit('progress', {'percent': 100})
```
