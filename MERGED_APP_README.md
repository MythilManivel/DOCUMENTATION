# 📄 AI-Powered Document Analysis - Merged Application

## Overview

This is a **unified Streamlit application** that combines the document UI from `document_ui/` with the complete RAG (Retrieval-Augmented Generation) backend from the `src/` folder.

### Features

✅ **Upload & Process PDFs** - Extract text, chunk, and generate embeddings
✅ **Generate Summaries** - Create structured business summaries of documents
✅ **Ask Questions** - Get answers based strictly on document content
✅ **Vector Search** - Find relevant information using semantic similarity

---

## What Was Merged

### Frontend (UI)
- **Source**: `document_ui/app_streamlit.py`
- Streamlit interface for document upload, summarization, and Q&A

### Backend (Processing)
- **PDF Extraction**: `src/pdf_extractor.py` - Extracts text from PDFs
- **Text Chunking**: `src/text_chunker.py` - Splits text into meaningful chunks
- **Embeddings**: `src/embeddings.py` - Generates vector embeddings using sentence transformers
- **Vector Store**: `src/vector_store.py` - Stores and searches embeddings using FAISS
- **Summarization**: `src/summarizer.py` - Creates business-focused summaries
- **Configuration**: `config/config.py` - Manages all settings

---

## How to Run

### Prerequisites
- Python 3.10+
- Virtual environment with dependencies installed

### Installation

1. **Ensure you have a virtual environment**:
```bash
python -m venv new_venv
.\new_venv\Scripts\Activate.ps1  # On Windows
```

2. **Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
pip install streamlit
```

### Running the Application

**From the root directory (`e:\rag\`):**

```bash
streamlit run merged_app.py
```

This will:
1. Start a local Streamlit server (typically on `http://localhost:8501`)
2. Open the application in your default browser
3. Display the AI-Powered Document Analysis interface

---

## Usage Workflow

### 1. **Upload & Process** 
- Click the upload button in the "📤 Upload & Process Document" section
- Select a PDF file
- Click "🚀 Upload & Process"
- The app will:
  - Extract text from the PDF
  - Chunk the text into manageable pieces
  - Generate embeddings for each chunk
  - Build a vector index for fast retrieval

### 2. **Generate Summary**
- Once a document is processed, navigate to "📋 Summarize Document"
- Click "📝 Generate Summary"
- View the structured summary with:
  - 🏢 Company Overview
  - 💰 Financial Performance
  - 📊 Profit / Loss
  - ⭐ Ratings / Grades
  - 🎯 Key Metrics & Highlights

### 3. **Ask Questions**
- In the "💬 Ask Questions About the Document" section
- Type your question (must be based on the document)
- Click "❓ Ask"
- The app uses RAG (Retrieval-Augmented Generation) to:
  - Convert your question to an embedding
  - Find the most relevant chunks
  - Return answers strictly from the document

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Streamlit UI (merged_app.py)                    │
│  Upload | Summarize | Ask Questions                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
   ┌────▼──────────┐  ┌─────────▼──────────┐
   │ PDF Extractor │  │  Text Chunker      │
   │ (PyPDF2 +     │  │  (Semantic/Fixed)  │
   │  pdfplumber)  │  └────────────────────┘
   └────────────────┘
        │
   ┌────▼──────────────────────┐
   │  Embedding Generator       │
   │  (Sentence Transformers)   │
   └────┬──────────────────────┘
        │
   ┌────▼──────────────────────┐
   │  Vector Store (FAISS)      │
   │  (Similarity Search)       │
   └────┬──────────────────────┘
        │
   ┌────▼──────────────────────┐
   │  QA Engine (DocumentQA)    │
   │  (Question Answering)      │
   └────────────────────────────┘
```

---

## Key Components

### **merged_app.py**
Main application file containing:
- `DocumentQA` class - RAG wrapper for question answering
- `process_pdf()` - Complete PDF processing pipeline
- `summarize_document()` - Summary generation
- `answer_question()` - Q&A functionality
- Streamlit UI components

### **Processing Pipeline**

1. **Upload** → Save to `data/uploads/`
2. **Extract** → PDF text extraction
3. **Chunk** → Split into 512-character chunks with overlap
4. **Embed** → Generate vector embeddings
5. **Index** → Store in FAISS vector database
6. **Query** → Convert questions to embeddings
7. **Retrieve** → Find top-3 similar chunks
8. **Answer** → Return relevant document content

---

## Session State Management

The application maintains:
- `doc_id` - Unique document identifier
- `document_text` - Full extracted text
- `chunks` - List of text chunks
- `vector_store` - FAISS index
- `embeddings_gen` - Embedding generator instance
- `qa_engine` - DocumentQA instance
- `summary` - Generated summary
- `chat_history` - Q&A conversation history

---

## Configuration

Settings are managed in `config/config.py`:

```python
CHUNK_SIZE = 512           # Characters per chunk
CHUNK_OVERLAP = 50         # Overlap between chunks
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
SIMILARITY_TOP_K = 3       # Top results for search
DEVICE = "cpu"             # or "cuda" for GPU
```

---

## File Structure

```
e:/rag/
├── merged_app.py                 # ← MAIN APPLICATION (Run this!)
├── requirements.txt
├── config/
│   └── config.py
├── src/
│   ├── pdf_extractor.py
│   ├── text_chunker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── summarizer.py
│   └── chatbot.py
├── document_ui/
│   ├── app_streamlit.py          # Original UI
│   ├── models/schemas.py
│   └── services/pipeline_adapter.py
└── data/
    └── uploads/                  # Where PDFs are stored
```

---

## Troubleshooting

### **PDF Not Processing**
- Ensure PDF is not corrupted
- Check file size (very large PDFs may need chunking)
- Check logs for specific extraction errors

### **Out of Memory**
- Reduce `CHUNK_SIZE` in config
- Process smaller documents
- Use `DEVICE = "cpu"` for GPU memory issues

### **Slow Embedding Generation**
- Use smaller embedding model (currently using all-MiniLM-L6-v2)
- Enable GPU with `DEVICE = "cuda"`
- Reduce document size

### **No Answers Found**
- Question may not match document content well
- Try rephrasing the question
- Check that document was processed successfully

---

## Performance Notes

- **First run**: Models download from HuggingFace (~2-3 GB)
- **PDF Processing**: ~30 seconds for 10-page document
- **Embedding**: ~2-5 seconds for 100 chunks
- **Q&A Response**: <1 second for similarity search

---

## Next Steps / Enhancements

- [ ] Add support for multiple document types (Word, Excel)
- [ ] Implement chat memory for multi-turn conversations
- [ ] Add citation tracking (which chunks answers come from)
- [ ] Support for image extraction from PDFs
- [ ] Batch document processing
- [ ] Export summaries and Q&A history

---

## Support

For issues or questions:
1. Check the logs in the browser console
2. Review the configuration in `config/config.py`
3. Verify all dependencies are installed

---

**Created**: December 31, 2025
**Status**: Fully Integrated & Ready to Use ✅
