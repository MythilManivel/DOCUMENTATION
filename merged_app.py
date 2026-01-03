"""
Integrated Document Analysis Application
Merges UI (Streamlit) with RAG backend for PDF processing, summarization, and QA
"""
import io
import sys
import os
from dataclasses import asdict
from pathlib import Path
from typing import Optional
import streamlit as st
import numpy as np
from uuid import uuid4

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure page first
st.set_page_config(
    page_title="📄 Document Analysis AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Show loading message while importing heavy modules
with st.spinner("🔄 Loading AI models... This may take a moment on first run."):
    try:
        from loguru import logger
        logger.disable("src")  # Disable noisy logging
    except:
        logger = None
    
    from src.pdf_extractor import PDFExtractor
    from src.text_chunker import TextChunker
    from src.embeddings import EmbeddingGenerator
    from src.vector_store import FAISSVectorStore
    from src.summarizer import BusinessSummarizer
    from config.config import (
        UPLOAD_DIR,
        CHUNK_SIZE,
        CHUNK_OVERLAP,
        EMBEDDING_MODEL,
        SUMMARIZATION_MODEL,
        DEVICE,
        SIMILARITY_TOP_K
    )

# Create uploads directory if it doesn't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Data Models
# ============================================================================

from pydantic import BaseModel

class DocumentSummary(BaseModel):
    """Structured business summary of a document"""
    company_overview: str
    financial_performance: str
    profit_loss: str
    ratings_grades: str
    key_metrics_highlights: str


# ============================================================================
# DocumentQA - Simple RAG wrapper
# ============================================================================

class DocumentQA:
    """Simple wrapper for document Q&A using vector store and embeddings"""
    
    def __init__(self, vector_store, embeddings, chunks):
        """Initialize QA engine with vector store, embeddings, and chunks"""
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.chunks = chunks
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question by finding relevant chunks and returning their content
        """
        if not question.strip():
            return "Please provide a valid question."
        
        try:
            # Generate embedding for the question
            question_embedding = self.embeddings.generate_embedding(question)
            
            # Search for similar chunks
            similar_chunks = self.vector_store.search(
                question_embedding,
                top_k=min(SIMILARITY_TOP_K, len(self.chunks))
            )
            
            if not similar_chunks:
                return "No relevant information found in the document."
            
            # Combine chunk texts as answer
            answer_texts = []
            for chunk_result in similar_chunks:
                if chunk_result.get("similarity_score", 0) > 0.3:
                    text = chunk_result.get("text", "")
                    if text:
                        answer_texts.append(text)
            
            if answer_texts:
                combined_answer = " ".join(answer_texts)
                return combined_answer[:1500]  # Limit answer length
            else:
                return "No relevant information found in the document."
                
        except Exception as e:
            safe_log(f"Error in QA: {e}", "error")
            return f"Error retrieving answer: {str(e)}"


# ============================================================================
# State Management
# ============================================================================

def safe_log(msg: str, level: str = "info"):
    """Safely log messages (graceful fallback if logger not available)"""
    if logger:
        try:
            if level == "info":
                logger.info(msg)
            elif level == "success":
                logger.success(msg)
            elif level == "error":
                logger.error(msg)
            elif level == "warning":
                logger.warning(msg)
        except:
            pass

def init_session_state() -> None:
    """Initialize Streamlit session state"""
    if "doc_id" not in st.session_state:
        st.session_state["doc_id"] = None
    if "uploaded_file_path" not in st.session_state:
        st.session_state["uploaded_file_path"] = None
    if "document_text" not in st.session_state:
        st.session_state["document_text"] = None
    if "chunks" not in st.session_state:
        st.session_state["chunks"] = None
    if "vector_store" not in st.session_state:
        st.session_state["vector_store"] = None
    if "embeddings_gen" not in st.session_state:
        st.session_state["embeddings_gen"] = None
    if "summary" not in st.session_state:
        st.session_state["summary"] = None
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "qa_engine" not in st.session_state:
        st.session_state["qa_engine"] = None


# ============================================================================
# Backend Processing Functions
# ============================================================================

def process_pdf(file_bytes: bytes, filename: str) -> tuple:
    """
    Process uploaded PDF file:
    1. Extract text from PDF
    2. Chunk the text
    3. Generate embeddings
    4. Store in vector database
    
    Returns: (doc_id, document_text, chunks, vector_store, embeddings_gen, qa_engine)
    """
    try:
        # 1. Extract text
        safe_log(f"Extracting text from {filename}")
        pdf_extractor = PDFExtractor()
        
        # Save file temporarily
        temp_path = UPLOAD_DIR / filename
        with open(temp_path, 'wb') as f:
            f.write(file_bytes)
        
        extraction_result = pdf_extractor.extract_text(str(temp_path))
        text = extraction_result.get("text", "")
        
        if not text or text.strip() == "":
            st.error("❌ Could not extract text from PDF. Please check the file.")
            return None, None, None, None, None, None
        
        safe_log(f"Extracted {extraction_result.get('word_count', 0)} words", "success")
        
        # 2. Chunk text
        safe_log("Chunking document")
        chunker = TextChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        chunks = chunker.chunk_text(text)
        
        if not chunks:
            st.error("❌ Could not chunk document text.")
            return None, None, None, None, None, None
        
        safe_log(f"Created {len(chunks)} chunks", "success")
        
        # 3. Generate embeddings
        safe_log("Generating embeddings")
        embedding_gen = EmbeddingGenerator(model_name=EMBEDDING_MODEL, device=DEVICE)
        chunks_with_embeddings = []
        
        progress_bar = st.progress(0)
        for idx, chunk in enumerate(chunks):
            try:
                embedding = embedding_gen.generate_embedding(chunk["text"])
                chunk["embedding"] = embedding
                chunks_with_embeddings.append(chunk)
                progress_bar.progress((idx + 1) / len(chunks))
            except Exception as e:
                safe_log(f"Error embedding chunk {idx}: {e}", "error")
                continue
        
        if not chunks_with_embeddings:
            st.error("❌ Could not generate embeddings for chunks.")
            return None, None, None, None, None, None
        
        safe_log(f"Generated embeddings for {len(chunks_with_embeddings)} chunks", "success")
        
        # 4. Store in vector database
        safe_log("Storing embeddings in vector store")
        vector_store = FAISSVectorStore(
            embedding_dimension=embedding_gen.embedding_dimension
        )
        vector_store.add_embeddings(chunks_with_embeddings, document_id=filename)
        safe_log("Vector store created", "success")
        
        # 5. Initialize QA engine
        safe_log("Initializing QA engine")
        qa_engine = DocumentQA(
            vector_store=vector_store,
            embeddings=embedding_gen,
            chunks=chunks_with_embeddings
        )
        safe_log("QA engine initialized", "success")
        
        # Generate doc_id
        doc_id = str(uuid4())
        
        return doc_id, text, chunks_with_embeddings, vector_store, embedding_gen, qa_engine
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        st.error(f"❌ Error processing PDF: {str(e)}")
        return None, None, None, None, None, None


def summarize_document(text: str) -> Optional[DocumentSummary]:
    """
    Generate structured business summary from document text
    """
    try:
        safe_log("Generating summary")
        summarizer = BusinessSummarizer(model_name=SUMMARIZATION_MODEL, device=DEVICE)
        
        # Split text into chunks for summarization if too long
        max_chunk_length = 1024
        text_chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
        
        summaries = []
        progress_bar = st.progress(0)
        
        for idx, chunk in enumerate(text_chunks[:5]):  # Summarize first 5 chunks
            if len(chunk.strip()) > 50:
                try:
                    summary = summarizer.generate_summary(chunk)
                    summaries.append(summary)
                except Exception as e:
                    safe_log(f"Could not summarize chunk {idx}: {e}", "warning")
                progress_bar.progress((idx + 1) / min(5, len(text_chunks)))
        
        combined_text = " ".join(summaries) if summaries else "Summary generation in progress..."
        
        # Extract business information
        doc_summary = DocumentSummary(
            company_overview=extract_company_overview(text),
            financial_performance=extract_financial_info(text),
            profit_loss=extract_profit_loss(text),
            ratings_grades=extract_ratings(text),
            key_metrics_highlights=combined_text if combined_text else "Key metrics extracted from document"
        )
        
        safe_log("Summary generated", "success")
        return doc_summary
        
    except Exception as e:
        safe_log(f"Error summarizing document: {e}", "error")
        st.error(f"❌ Error summarizing document: {str(e)}")
        return None


def answer_question(qa_engine, question: str) -> Optional[str]:
    """
    Answer a question based on the uploaded document using RAG
    """
    try:
        if qa_engine is None:
            return "Please upload and process a document first."
        
        safe_log(f"Answering question: {question}")
        answer = qa_engine.answer_question(question)
        
        if not answer or answer.strip() == "":
            return "The information requested is not available in the uploaded document."
        
        safe_log("Question answered", "success")
        return answer
        
    except Exception as e:
        safe_log(f"Error answering question: {e}", "error")
        return f"Error answering question: {str(e)}"


# ============================================================================
# Helper Functions for Summary Extraction
# ============================================================================

def extract_company_overview(text: str) -> str:
    """Extract company overview from text"""
    lines = text.split('\n')[:15]
    overview = " ".join([line for line in lines if len(line.strip()) > 10])
    return overview[:500] if overview else "Company information extracted from document"


def extract_financial_info(text: str) -> str:
    """Extract financial performance information"""
    text_upper = text.upper()
    keywords = ["REVENUE", "PROFIT", "INCOME", "EARNINGS", "SALES", "FINANCIAL"]
    
    results = []
    for keyword in keywords:
        if keyword in text_upper:
            idx = text_upper.find(keyword)
            snippet = text[max(0, idx-30):idx+100]
            if snippet.strip():
                results.append(snippet)
    
    return " ".join(results)[:500] if results else "Financial data not found in document"


def extract_profit_loss(text: str) -> str:
    """Extract profit/loss information"""
    text_upper = text.upper()
    keywords = ["PROFIT", "LOSS", "NET INCOME", "OPERATING INCOME", "EBITDA"]
    
    results = []
    for keyword in keywords:
        if keyword in text_upper:
            idx = text_upper.find(keyword)
            snippet = text[max(0, idx-30):idx+100]
            if snippet.strip():
                results.append(snippet)
    
    return " ".join(results)[:500] if results else "Profit/Loss data not found in document"


def extract_ratings(text: str) -> str:
    """Extract ratings or grades from text"""
    import re
    
    rating_patterns = [
        r'rating[:\s]+([A-Z+\-0-9.]+)',
        r'grade[:\s]+([A-Z+\-0-9.]+)',
        r'score[:\s]+([0-9.]+)',
    ]
    
    results = []
    for pattern in rating_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            results.append(match.group(0))
    
    return " ".join(results)[:500] if results else "No ratings or grades found in document"


# ============================================================================
# UI Components
# ============================================================================

def render_upload_section():
    """Render the upload and process section"""
    st.header("📤 Upload & Process Document")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a PDF document",
            type=["pdf"],
            help="Select a PDF file to analyze"
        )
    
    if st.button("🚀 Upload & Process", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.warning("⚠️ Please upload a PDF file before processing.")
            return
        
        with st.spinner("🔄 Processing document (extracting text, chunking, embedding, indexing)..."):
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name
            
            doc_id, text, chunks, vector_store, embedding_gen, qa_engine = process_pdf(
                file_bytes=file_bytes,
                filename=file_name
            )
            
            if doc_id:
                # Store in session state
                st.session_state["doc_id"] = doc_id
                st.session_state["uploaded_file_path"] = file_name
                st.session_state["document_text"] = text
                st.session_state["chunks"] = chunks
                st.session_state["vector_store"] = vector_store
                st.session_state["embeddings_gen"] = embedding_gen
                st.session_state["qa_engine"] = qa_engine
                st.session_state["summary"] = None
                st.session_state["chat_history"] = []
                
                st.success(f"✅ Document processed successfully! ({len(chunks)} chunks created)")
                st.info(f"📊 Document size: {len(text):,} characters")
            else:
                st.error("❌ Failed to process PDF. Please check the file format.")


def render_summary_section():
    """Render the summarization section"""
    st.header("📋 Summarize Document")
    
    disabled = st.session_state.get("doc_id") is None
    
    if st.button(
        "📝 Generate Summary",
        disabled=disabled,
        type="secondary",
        use_container_width=True
    ):
        if disabled:
            st.warning("⚠️ Please upload and process a document first.")
            return
        
        with st.spinner("⏳ Generating structured business summary..."):
            summary = summarize_document(st.session_state.get("document_text", ""))
            st.session_state["summary"] = summary
    
    summary = st.session_state.get("summary")
    if summary is not None:
        st.subheader("Summary Results")
        
        # Convert to dict if needed
        if hasattr(summary, 'model_dump'):
            data = summary.model_dump()
        elif hasattr(summary, 'dict'):
            data = summary.dict()
        elif hasattr(summary, '__dataclass_fields__'):
            data = asdict(summary)
        else:
            data = dict(summary) if isinstance(summary, dict) else {}
        
        # Display summary sections
        with st.expander("🏢 Company Overview", expanded=True):
            st.write(data.get("company_overview", "-"))
        
        with st.expander("💰 Financial Performance"):
            st.write(data.get("financial_performance", "-"))
        
        with st.expander("📊 Profit / Loss"):
            st.write(data.get("profit_loss", "-"))
        
        with st.expander("⭐ Ratings / Grades"):
            st.write(data.get("ratings_grades", "-"))
        
        with st.expander("🎯 Key Metrics & Highlights", expanded=True):
            st.write(data.get("key_metrics_highlights", "-"))


def render_chatbot_section():
    """Render the Q&A section"""
    st.header("💬 Ask Questions About the Document")
    
    disabled = st.session_state.get("doc_id") is None
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        question = st.text_input(
            "Your question",
            placeholder="Ask something strictly based on the uploaded document...",
            disabled=disabled
        )
    
    if st.button(
        "❓ Ask",
        disabled=disabled or not question.strip(),
        type="secondary",
        use_container_width=True
    ):
        if disabled:
            st.warning("⚠️ Please upload and process a document first.")
            return
        
        if not question.strip():
            st.warning("⚠️ Please enter a question.")
            return
        
        with st.spinner("🔍 Retrieving answer from document..."):
            qa_engine = st.session_state.get("qa_engine")
            answer = answer_question(qa_engine, question)
        
        if answer:
            st.session_state["chat_history"].append({
                "question": question,
                "answer": answer
            })
    
    # Display chat history
    if st.session_state.get("chat_history"):
        st.subheader("💭 Conversation History")
        for idx, turn in enumerate(st.session_state["chat_history"], start=1):
            with st.expander(f"Q{idx}: {turn['question'][:60]}..."):
                st.markdown(f"**Question:** {turn['question']}")
                st.markdown(f"**Answer:** {turn['answer']}")


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application function"""
    # st.set_page_config is already called at the top during imports
    
    # Initialize session state
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("📚 Document Analysis")
        st.markdown("---")
        
        if st.session_state.get("doc_id"):
            st.success(f"✅ Document Loaded")
            st.write(f"**File:** {st.session_state.get('uploaded_file_path', 'Unknown')}")
            text_len = len(st.session_state.get('document_text', '') or '')
            st.write(f"**Size:** {text_len:,} characters")
            
            if st.button("🔄 Reset Document", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        else:
            st.info("👉 Upload a PDF to get started")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "This integrated app combines RAG (Retrieval-Augmented Generation) with "
            "document analysis to:\n"
            "- 📄 Extract and process PDF content\n"
            "- 📋 Generate structured summaries\n"
            "- ❓ Answer questions based on document content"
        )
    
    # Main content
    st.title("🤖 AI-Powered Document Analysis")
    st.caption(
        "Upload a PDF, generate a structured business summary, "
        "and ask precise questions based on the document content."
    )
    
    st.markdown("---")
    render_upload_section()
    
    st.markdown("---")
    render_summary_section()
    
    st.markdown("---")
    render_chatbot_section()


if __name__ == "__main__":
    main()
