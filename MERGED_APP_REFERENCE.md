# ⚡ Merged App - Quick Reference Card

## 🎯 What Changed?

| Item | Before | After |
|------|--------|-------|
| **Structure** | 2 separate applications | 1 unified app |
| **Main File** | `document_ui/app_streamlit.py` | `merged_app.py` |
| **Backend** | Scattered in `src/` | Integrated in one file |
| **Run Command** | N/A - couldn't run standalone | `streamlit run merged_app.py` |

---

## 🚀 To Start Using

```bash
# 1. Go to project
cd e:\rag

# 2. Activate environment  
.\new_venv\Scripts\Activate.ps1

# 3. Run app
streamlit run merged_app.py
```

---

## 📋 Features & Usage

### 1️⃣ **Upload Section**
```
Location: Top of app
Action: Click "🚀 Upload & Process"
Result: Document stored, indexed, ready for analysis
Time: 30-60 seconds
```

### 2️⃣ **Summarize Section**
```
Location: Middle of app
Action: Click "📝 Generate Summary"
Result: See company, financial, profit/loss, ratings, metrics
Time: 10-30 seconds
```

### 3️⃣ **Ask Questions Section**
```
Location: Bottom of app
Action: Type question → Click "❓ Ask"
Result: Get answer from document
Time: <1 second
```

---

## 🎨 UI Elements

| Element | Purpose | Location |
|---------|---------|----------|
| 📤 Upload Button | Select PDF file | Top section |
| 🚀 Process Button | Start processing | Top section |
| 📝 Summary Button | Generate summary | Middle section |
| ❓ Ask Button | Answer question | Bottom section |
| 🔄 Reset Button | Clear document | Sidebar |

---

## 📊 What Happens Behind Scenes

```
Upload PDF
    ↓
Extract Text (pdf_extractor.py)
    ↓
Split Chunks (text_chunker.py)
    ↓
Generate Embeddings (embeddings.py)
    ↓
Index in FAISS (vector_store.py)
    ↓
Ready for Q&A (chatbot.py/DocumentQA)
```

---

## ⚙️ Configuration (if needed)

**File**: `config/config.py`

Common settings:
```python
CHUNK_SIZE = 512              # Size of text chunks
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Embedding model
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
DEVICE = "cpu"                # Change to "cuda" for GPU
```

---

## 🔧 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Module not found | `pip install -r requirements.txt` |
| Port in use | `streamlit run merged_app.py --server.port 8502` |
| Slow processing | Set `DEVICE = "cpu"` in config |
| PDF won't extract | Try different PDF or smaller file |
| No answers found | Rephrase question, ensure PDF processed |

---

## 📁 Project Structure

```
e:\rag\
├── merged_app.py          ← MAIN FILE (the merged app)
├── config/config.py       ← Settings
├── src/                   ← Backend modules
│   ├── pdf_extractor.py
│   ├── text_chunker.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── summarizer.py
│   └── chatbot.py
└── data/uploads/          ← Uploaded PDFs
```

---

## 💡 Pro Tips

1. **First run takes time** → Models download from internet (2-3 GB)
2. **Large PDFs?** → Split into smaller documents
3. **Better answers?** → Ask specific questions
4. **Multiple docs?** → Use reset button between uploads
5. **Need GPU?** → Set `DEVICE = "cuda"` in config

---

## 📞 Support Info

- **Logs**: Check browser console (F12) for errors
- **Dependencies**: Run `pip install -r requirements.txt` if issues
- **Stuck?**: Try restarting app (Ctrl+C, then run again)

---

## ✨ What's New

🎨 Enhanced UI with emojis and better layout
🔍 Integrated RAG for better answers
💬 Conversation history tracking
📊 Progress bars for long operations
⚠️ Better error messages
🔄 Seamless document reset

---

## 📚 Full Documentation

- **QUICK_START_MERGED.md** - Step-by-step guide
- **MERGED_APP_README.md** - Technical deep dive
- **MERGE_COMPLETED.md** - Complete summary

---

## 🎯 Next Steps

```
1. Open terminal
2. cd e:\rag
3. .\new_venv\Scripts\Activate.ps1
4. streamlit run merged_app.py
5. Upload a PDF
6. Click "Process"
7. Click "Summarize"
8. Ask questions
9. Done! 🎉
```

---

**All merged. All working. Ready to go! ✅**
