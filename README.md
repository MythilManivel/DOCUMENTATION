# AI-Powered Document Analysis System with RAG

A comprehensive Python-based system for intelligent document analysis using Natural Language Processing, Machine Learning, and Retrieval-Augmented Generation (RAG).

## 🎯 Project Overview

This system allows users to:
1. Upload PDF documents (5-7 pages)
2. Automatically generate structured business summaries highlighting:
   - Company overview
   - Financial performance (Profit/Loss)
   - Ratings and grades
   - Key metrics and highlights
3. Interact with an AI chatbot that answers questions based **ONLY** on the document content (no hallucination)

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PDF DOCUMENT INPUT                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              PDF TEXT EXTRACTION                             │
│          (PyPDF2 + pdfplumber)                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              TEXT CHUNKING                                   │
│     (Semantic chunking with overlap)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            EMBEDDING GENERATION                              │
│   (sentence-transformers/all-MiniLM-L6-v2)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
┌─────────────────────┐ ┌─────────────────────────────────┐
│  VECTOR DATABASE    │ │  BUSINESS SUMMARIZATION         │
│  (FAISS Index)      │ │  (BART-large-CNN)              │
│                     │ │                                 │
│  - Similarity Search│ │  - Company Overview             │
│  - Context Retrieval│ │  - Financial Performance        │
└──────────┬──────────┘ │  - Key Metrics                  │
           │            │  - Ratings/Grades               │
           │            └─────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│              RAG CHATBOT (Q&A)                              │
│    1. Query → Embedding                                     │
│    2. Retrieve relevant chunks (Vector Search)              │
│    3. Generate answer (RoBERTa-SQuAD2)                     │
│    4. Validate (confidence threshold)                       │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Technical Stack

### Core Libraries

| Component | Library | Purpose |
|-----------|---------|---------|
| **PDF Processing** | PyPDF2, pdfplumber | Extract text from PDF documents |
| **NLP/ML** | Transformers, Torch | Transformer models for NLP tasks |
| **Embeddings** | sentence-transformers | Generate vector embeddings |
| **Vector DB** | FAISS | Efficient similarity search |
| **Summarization** | facebook/bart-large-cnn | Text summarization |
| **Q&A** | deepset/roberta-base-squad2 | Question answering |
| **Utilities** | NumPy, Pandas, Loguru | Data processing and logging |

### Models Used

1. **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
   - Fast, efficient, 384-dimensional embeddings
   - Optimized for semantic similarity

2. **Summarization Model**: `facebook/bart-large-cnn`
   - State-of-the-art abstractive summarization
   - Pre-trained on CNN/DailyMail dataset

3. **Q&A Model**: `deepset/roberta-base-squad2`
   - Fine-tuned for extractive question answering
   - Handles "unanswerable" questions

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 4GB+ RAM recommended
- (Optional) CUDA-enabled GPU for faster processing

### Step 1: Clone or Download Project

```bash
cd E:\rag
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First run will download ML models (~2GB), which may take some time.

### Step 4: Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env file to customize settings
```

## 🚀 Usage

### Quick Start

Process a PDF document:

```bash
python main.py path/to/document.pdf
```

This will:
1. Extract text from the PDF
2. Generate a structured business summary
3. Start an interactive Q&A session

### Command-Line Options

```bash
# Get summary only (skip Q&A)
python main.py document.pdf --summary-only

# Ask a specific question
python main.py document.pdf -q "What is the revenue?"

# Load previous session
python main.py --load-state
```

### Programmatic Usage

```python
from main import DocumentAnalyzer
from pathlib import Path

# Initialize system
analyzer = DocumentAnalyzer()

# Process document
result = analyzer.process_document(Path("document.pdf"))

# Get summary
print(result["summary"])

# Ask questions
answer = analyzer.ask_question("What is the profit margin?")
print(answer["answer"])
print(f"Confidence: {answer['confidence']:.2%}")

# Interactive session
analyzer.start_interactive_session()
```

## 📊 Project Structure

```
rag/
├── config/
│   └── config.py              # Configuration settings
├── src/
│   ├── pdf_extractor.py       # PDF text extraction
│   ├── text_chunker.py        # Text chunking logic
│   ├── embeddings.py          # Embedding generation
│   ├── vector_store.py        # FAISS vector database
│   ├── summarizer.py          # Business summarization
│   ├── chatbot.py             # RAG chatbot implementation
│   └── utils.py               # Utility functions
├── data/
│   ├── uploads/               # Uploaded PDFs
│   └── processed/             # Processed data
├── models/                    # Saved models and indices
├── tests/                     # Unit tests
├── docs/                      # Additional documentation
├── main.py                    # Main application
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🔬 Technical Details

### 1. PDF Text Extraction

Uses dual strategy for robust extraction:
- **Primary**: pdfplumber (better for complex layouts)
- **Fallback**: PyPDF2 (faster, simpler documents)

### 2. Text Chunking

Implements semantic chunking to preserve context:
- Default chunk size: 500 characters
- Overlap: 100 characters
- Preserves paragraph and sentence boundaries

### 3. Embedding Generation

Converts text to dense vector representations:
- Model: all-MiniLM-L6-v2 (384 dimensions)
- Batch processing for efficiency
- Cosine similarity for search

### 4. Vector Database (FAISS)

Efficient similarity search:
- IndexFlatL2 for exact search
- Stores chunk metadata alongside vectors
- Supports document-level filtering

### 5. Business Summarization

Generates structured summaries:
- Extracts business-relevant sections using keyword matching
- Focuses on financial metrics, ratings, highlights
- Regex-based metric extraction (currency, percentages, grades)

### 6. RAG Chatbot

Retrieval-Augmented Generation pipeline:

**Step 1**: Query embedding
- Converts user question to vector

**Step 2**: Retrieval
- Searches vector database for relevant chunks
- Returns top-k most similar contexts

**Step 3**: Answer Generation
- Uses retrieved context as input to Q&A model
- Generates answer from context only

**Step 4**: Validation
- Checks confidence score
- Ensures answer is grounded in document
- Rejects low-confidence answers

**Anti-Hallucination Measures**:
- Only uses retrieved document context
- Confidence threshold (default: 30%)
- Context overlap validation
- No external knowledge injection

## 📈 Performance Considerations

### Speed Optimization
- Batch embedding generation
- Efficient vector search with FAISS
- Model caching and reuse
- Optional GPU acceleration

### Memory Management
- Streaming for large documents
- Chunk-based processing
- Model quantization available

### Scalability
- Modular architecture
- Easy to swap models
- Database persistence
- Stateless API design

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_pdf_extractor.py

# With coverage
pytest --cov=src tests/
```

## 🎓 Educational Value (Final Year Project)

### Key Learning Outcomes

1. **NLP & ML Concepts**
   - Text preprocessing and tokenization
   - Word embeddings and semantic similarity
   - Transformer architectures
   - Transfer learning with pre-trained models

2. **RAG Architecture**
   - Vector databases and similarity search
   - Retrieval-augmented generation
   - Hallucination prevention
   - Context-aware answer generation

3. **Software Engineering**
   - Modular design patterns
   - Error handling and logging
   - Configuration management
   - Testing and validation

4. **Practical Applications**
   - Document intelligence
   - Automated summarization
   - Conversational AI
   - Business analytics

### Demonstration Points

1. **Technical Depth**
   - Multiple ML models integration
   - Vector database implementation
   - End-to-end pipeline design

2. **Innovation**
   - Business-focused summarization
   - Anti-hallucination measures
   - Structured output format

3. **Usability**
   - CLI and programmatic interfaces
   - Interactive chat session
   - Clear documentation

## 🔐 Best Practices

1. **Environment Variables**: Use `.env` for sensitive configuration
2. **Logging**: Comprehensive logging for debugging
3. **Error Handling**: Graceful failures with informative messages
4. **Code Quality**: Type hints, docstrings, PEP 8 compliance
5. **Modularity**: Separate concerns, easy to extend

## 📝 Sample Input/Output

### Input
A 5-page PDF document about a company's quarterly financial report.

### Output - Structured Summary
```
**Company Overview:**
TechCorp Inc. is a leading AI technology company specializing in cloud solutions.

**Financial Performance:**
Q4 2023 revenue reached $500M (25% YoY growth). Net profit margin improved to 15%.

**Key Metrics:**
• Revenue: $500 million • Growth: 25% YoY • Profit margin: 15%

**Ratings & Grades:**
Industry analysts awarded an A+ rating for innovation potential.

**Key Highlights:**
Successful AI platform launch with 10,000 new customers.
```

### Output - Q&A Examples
```
Q: What was the revenue growth?
A: The revenue increased by 25% year-over-year.
Confidence: 94.2%

Q: What is the profit margin?
A: The net profit margin improved to 15%.
Confidence: 89.7%
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Models not downloading
- **Solution**: Check internet connection, retry with `pip install --upgrade transformers`

**Issue**: Out of memory errors
- **Solution**: Reduce batch size in `config.py`, close other applications

**Issue**: Slow processing
- **Solution**: Use GPU if available (set `DEVICE=cuda` in `.env`)

**Issue**: Poor quality summaries
- **Solution**: Adjust `SUMMARY_MAX_LENGTH` and business keywords in `config.py`

## 📚 References

- [Transformers Documentation](https://huggingface.co/docs/transformers)
- [FAISS Documentation](https://faiss.ai/)
- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [Sentence Transformers](https://www.sbert.net/)

## 📄 License

This project is created for educational purposes as a final year engineering project.

## 👥 Author

**Your Name**
- Final Year Student
- [Your University/College]
- Engineering Department

## 🙏 Acknowledgments

- HuggingFace for pre-trained models
- Facebook AI Research for FAISS
- Open-source community

---

**Note**: This is an educational project demonstrating RAG, NLP, and ML concepts. For production use, consider additional security, scalability, and performance optimizations.
