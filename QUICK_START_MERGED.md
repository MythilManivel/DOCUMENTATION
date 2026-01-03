# ⚡ Quick Start Guide - Merged Document Analysis App

## 🚀 Get Started in 3 Steps

### Step 1: Activate Virtual Environment
```bash
cd e:\rag
.\new_venv\Scripts\Activate.ps1
```

### Step 2: Run the Application
```bash
streamlit run merged_app.py
```

### Step 3: Upload a PDF
1. Open your browser (typically opens automatically at `http://localhost:8501`)
2. Upload a PDF file using the file uploader
3. Click "🚀 Upload & Process" button

---

## 📋 What You Can Do

### Upload & Store Documents
✅ Click "🚀 Upload & Process"
- Extracts text from PDF
- Creates embeddings
- Stores in vector database

### Summarize Documents
✅ Click "📝 Generate Summary"
- Company Overview
- Financial Performance
- Profit/Loss Analysis
- Ratings & Grades
- Key Metrics

### Ask Questions
✅ Type your question, click "❓ Ask"
- Get answers from document
- See conversation history
- Ask follow-up questions

---

## 🎯 Example Workflow

```
1. Upload PDF
   ↓
2. Click "Upload & Process" (wait for completion)
   ↓
3. Click "Generate Summary" (read the summary)
   ↓
4. Ask questions like:
   - "What is the company revenue?"
   - "Who are the key management?"
   - "What are the main products?"
```

---

## 📁 Application File

**Location**: `e:\rag\merged_app.py`

This single file contains:
- Complete UI (Streamlit)
- All backend processing
- Document analysis pipeline
- Question answering engine

No need to use `document_ui/` or separate backends anymore!

---

## ⚙️ If Errors Occur

### Error: "Module not found"
```bash
pip install -r requirements.txt
pip install streamlit
```

### Error: "Port 8501 already in use"
```bash
streamlit run merged_app.py --server.port 8502
```

### Error: "CUDA/GPU issue"
```python
# Edit config/config.py, set:
DEVICE = "cpu"  # Use CPU instead
```

---

## 📊 Features

| Feature | Status |
|---------|--------|
| PDF Upload | ✅ Enabled |
| Text Extraction | ✅ Enabled |
| Summarization | ✅ Enabled |
| Question Answering | ✅ Enabled |
| Chat History | ✅ Enabled |
| Vector Search | ✅ Enabled |

---

## 🔗 Architecture Diagram

```
User Interface (Streamlit)
         ↓
    PDF Upload
         ↓
 ┌─────────────────┐
 │ PDF Extractor   │
 │ Text Chunker    │
 │ Embeddings      │ ← RAG Pipeline
 │ Vector Store    │
 │ Summarizer      │
 │ QA Engine       │
 └─────────────────┘
         ↓
    Results Display
```

---

## 💡 Tips

1. **First time?** The app will download models (~2GB) on first run
2. **Large PDFs?** Split into smaller documents for faster processing
3. **Better answers?** Ask specific questions matching document content
4. **Want to reset?** Click "🔄 Reset Document" button in sidebar

---

## 📞 Support

If something doesn't work:
1. Check if virtual environment is activated
2. Ensure all dependencies installed: `pip install -r requirements.txt`
3. Check browser console for errors (F12)
4. Try restarting: Ctrl+C, then run command again

---

**You're all set! 🎉 Run `streamlit run merged_app.py` and start analyzing documents!**
