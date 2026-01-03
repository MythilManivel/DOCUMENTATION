"""
Main Application Entry Point
AI-Powered Document Analysis System with RAG
"""
from pathlib import Path
import sys
sys.path.append('src')

from src.pdf_extractor import PDFExtractor
from src.text_chunker import TextChunker
from src.embeddings import EmbeddingGenerator
from src.vector_store import DocumentStore
from src.summarizer import BusinessSummarizer
from src.chatbot import RAGChatbot, InteractiveChatbot
from src.utils import (
    setup_logger, generate_document_id, validate_pdf_file,
    print_section, print_summary_table, Timer
)
from config.config import LOG_FILE, LOG_LEVEL
from loguru import logger


class DocumentAnalyzer:
    """
    Main document analysis system integrating all components
    """
    
    def __init__(self):
        """Initialize the document analyzer system"""
        # Setup logging
        setup_logger(LOG_FILE, LOG_LEVEL)
        logger.info("Initializing Document Analyzer System")
        
        # Initialize components
        logger.info("Loading models (this may take a moment)...")
        
        self.pdf_extractor = PDFExtractor()
        self.text_chunker = TextChunker()
        self.embedding_generator = EmbeddingGenerator()
        self.document_store = DocumentStore(
            self.embedding_generator.get_embedding_dimension()
        )
        self.summarizer = BusinessSummarizer()
        self.chatbot = RAGChatbot(self.embedding_generator, self.document_store)
        self.interactive_chatbot = InteractiveChatbot(self.chatbot)
        
        self.current_document_id = None
        
        logger.success("Document Analyzer initialized successfully!")
    
    def process_document(self, pdf_path: Path) -> dict:
        """
        Process a PDF document through the complete pipeline
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing document: {pdf_path}")
        
        # Validate file
        is_valid, error = validate_pdf_file(pdf_path)
        if not is_valid:
            logger.error(f"Invalid PDF file: {error}")
            return {"success": False, "error": error}
        
        # Generate document ID
        doc_id = generate_document_id(pdf_path)
        self.current_document_id = doc_id
        self.interactive_chatbot.set_active_document(doc_id)
        
        try:
            # Step 1: Extract text from PDF
            with Timer("PDF text extraction"):
                extraction_result = self.pdf_extractor.extract_text(pdf_path)
                extracted_text = extraction_result["text"]
            
            # Step 2: Chunk text
            with Timer("Text chunking"):
                chunks = self.text_chunker.chunk_text(extracted_text, method="semantic")
            
            # Step 3: Generate embeddings
            with Timer("Embedding generation"):
                chunks_with_embeddings = self.embedding_generator.generate_embeddings_for_chunks(chunks)
            
            # Step 4: Store in vector database
            with Timer("Vector database storage"):
                self.document_store.add_document(
                    document_id=doc_id,
                    full_text=extracted_text,
                    chunks_with_embeddings=chunks_with_embeddings
                )
            
            # Step 5: Generate summary
            with Timer("Business summary generation"):
                structured_summary = self.summarizer.generate_structured_summary(extracted_text)
            
            logger.success(f"Document {doc_id} processed successfully!")
            
            return {
                "success": True,
                "document_id": doc_id,
                "text": extracted_text,
                "chunks_count": len(chunks),
                "summary": structured_summary,
                "metadata": extraction_result["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {"success": False, "error": str(e)}
    
    def get_summary(self, format_type: str = "structured") -> dict:
        """
        Get summary of the current document
        
        Args:
            format_type: "structured" or "concise"
            
        Returns:
            Summary dictionary
        """
        if not self.current_document_id:
            return {"error": "No document loaded"}
        
        doc = self.document_store.get_document(self.current_document_id)
        if not doc:
            return {"error": "Document not found"}
        
        if format_type == "structured":
            summary = self.summarizer.generate_structured_summary(doc["full_text"])
        else:
            summary = self.summarizer.generate_concise_summary(doc["full_text"])
        
        return {"summary": summary}
    
    def ask_question(self, question: str) -> dict:
        """
        Ask a question about the current document
        
        Args:
            question: User's question
            
        Returns:
            Answer dictionary with 'answer' and 'confidence' keys, or 'error' key if failed
        """
        if not self.current_document_id:
            return {
                "answer": "No document loaded. Please upload a document first.",
                "confidence": 0.0,
                "error": "No document loaded"
            }
        
        result = self.chatbot.get_detailed_answer(
            question,
            document_id=self.current_document_id
        )
        
        return result
    
    def start_interactive_session(self):
        """Start an interactive Q&A session"""
        if not self.current_document_id:
            print("Error: No document loaded. Please process a document first.")
            return
        
        self.interactive_chatbot.start_session()
    
    def save_state(self):
        """Save current state to disk"""
        logger.info("Saving document store...")
        self.document_store.save_all()
        logger.success("State saved successfully")
    
    def load_state(self):
        """Load state from disk"""
        logger.info("Loading document store...")
        success = self.document_store.load_all()
        if success:
            logger.success("State loaded successfully")
        else:
            logger.warning("No saved state found")
        return success


def demo_workflow(pdf_path: Path):
    """
    Demonstration workflow showing complete system capabilities
    
    Args:
        pdf_path: Path to a sample PDF document
    """
    print_section("AI-POWERED DOCUMENT ANALYSIS SYSTEM", 70)
    print("Initializing system...\n")
    
    # Initialize system
    analyzer = DocumentAnalyzer()
    
    print_section("STEP 1: DOCUMENT UPLOAD & PROCESSING", 70)
    print(f"Processing document: {pdf_path.name}")
    
    # Process document
    result = analyzer.process_document(pdf_path)
    
    if not result["success"]:
        print(f"Error: {result['error']}")
        return
    
    print(f"\n✓ Document processed successfully!")
    print(f"  Document ID: {result['document_id']}")
    print(f"  Extracted: {result['metadata'].get('num_pages', 'N/A')} pages")
    print(f"  Word count: {len(result['text'].split())} words")
    print(f"  Created: {result['chunks_count']} text chunks")
    
    # Display summary
    print_section("STEP 2: BUSINESS SUMMARY", 70)
    
    summary = result["summary"]
    formatted_summary = analyzer.summarizer.format_summary_output(summary)
    print(formatted_summary)
    
    # Q&A demonstration
    print_section("STEP 3: INTERACTIVE Q&A (RAG CHATBOT)", 70)
    print("The system can now answer questions based ONLY on the uploaded document.")
    print("No external knowledge or hallucination - all answers are grounded in the document.\n")
    
    # Example questions
    sample_questions = [
        "What is the company overview?",
        "What is the financial performance?",
        "What are the key metrics?"
    ]
    
    print("Example questions:\n")
    for i, q in enumerate(sample_questions, 1):
        print(f"{i}. {q}")
        answer_result = analyzer.ask_question(q)
        print(f"   Answer: {answer_result['answer']}")
        print(f"   Confidence: {answer_result['confidence']:.2%}\n")
    
    # Start interactive session
    print_section("INTERACTIVE SESSION", 70)
    print("Starting interactive Q&A session...")
    print("You can now ask your own questions!\n")
    
    analyzer.start_interactive_session()
    
    # Save state
    print_section("SAVING STATE", 70)
    analyzer.save_state()
    print("System state saved. You can reload it in future sessions.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI-Powered Document Analysis System with RAG"
    )
    parser.add_argument(
        "pdf_file",
        type=str,
        nargs="?",
        help="Path to PDF file to analyze"
    )
    parser.add_argument(
        "--question",
        "-q",
        type=str,
        help="Ask a specific question (requires loaded document)"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only generate summary, skip Q&A"
    )
    parser.add_argument(
        "--load-state",
        action="store_true",
        help="Load previously saved state"
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = DocumentAnalyzer()
    
    # Load state if requested
    if args.load_state:
        analyzer.load_state()
    
    # Process PDF if provided
    if args.pdf_file:
        pdf_path = Path(args.pdf_file)
        
        if not pdf_path.exists():
            print(f"Error: File not found: {pdf_path}")
            return
        
        print_section("PROCESSING DOCUMENT", 70)
        result = analyzer.process_document(pdf_path)
        
        if not result["success"]:
            print(f"Error: {result['error']}")
            return
        
        print("✓ Document processed successfully!\n")
        
        # Display summary
        print_section("DOCUMENT SUMMARY", 70)
        formatted_summary = analyzer.summarizer.format_summary_output(result["summary"])
        print(formatted_summary)
        
        # Handle specific question
        if args.question:
            print_section("QUESTION & ANSWER", 70)
            print(f"Q: {args.question}\n")
            answer = analyzer.ask_question(args.question)
            print(f"A: {answer['answer']}")
            print(f"\nConfidence: {answer['confidence']:.2%}")
        
        # Start interactive session unless summary-only
        elif not args.summary_only:
            print_section("INTERACTIVE Q&A SESSION", 70)
            analyzer.start_interactive_session()
        
        # Save state
        analyzer.save_state()
    
    else:
        # No PDF provided, show help
        parser.print_help()
        print("\n" + "="*70)
        print("EXAMPLE USAGE:")
        print("="*70)
        print("\n1. Process a document and start interactive Q&A:")
        print("   python main.py path/to/document.pdf")
        print("\n2. Process and get summary only:")
        print("   python main.py path/to/document.pdf --summary-only")
        print("\n3. Ask a specific question:")
        print('   python main.py path/to/document.pdf -q "What is the revenue?"')
        print("\n4. Load previous session:")
        print("   python main.py --load-state")
        print()


if __name__ == "__main__":
    main()
