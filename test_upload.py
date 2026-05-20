"""
Test script to upload a PDF and process it through the OCR pipeline.
"""
# pyrefly: ignore [missing-import]
import httpx
import time
import sys
import io

# Force UTF-8 output to prevent Windows console emoji crashes
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

def create_test_pdf():
    """Create a simple test PDF using PyMuPDF"""
    try:
        # type: ignore
        # pyrefly: ignore [missing-import]
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        
        # Create an invoice-like document
        text = """INVOICE #INV-2024-001
        
        Date: 2024-01-15
        Amount: $1,250.00
        Vendor: TechCorp Solutions
        Customer: John Doe
        
        Description: Software Development Services
        Quantity: 10 hours
        Rate: $125.00/hour
        
        Payment Due: 2024-02-15"""
        
        page.insert_text((72, 72), text, fontsize=12)
        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes
    except ImportError:
        # Fallback: create a simple PDF manually
        print("PyMuPDF not available, creating minimal PDF...")
        return b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>\nstream\nINVOICE #INV-2024-001\nVendor: TechCorp Solutions\nCustomer: John Doe\nAmount: $1,250.00\nendstream\nendobj\nxref\n0 4\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n0\n%%EOF"

def main():
    print("Creating test PDF...")
    pdf_content = create_test_pdf()
    filename = "test_invoice.pdf"
    
    # Step 1: Upload
    print("\n📤 Step 1: Uploading PDF...")
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/upload",
            files={"file": (filename, pdf_content, "application/pdf")}
        )
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.text}")
            sys.exit(1)
        
        data = response.json()
        job_id = data["job_id"]
        print(f"✅ Upload successful!")
        print(f"   Job ID: {job_id}")
        print(f"   Pages: {data['page_count']}")
        print(f"   Status: {data['status']}")
        
        # Step 2: Process
        print(f"\n⚙️  Step 2: Starting processing pipeline...")
        response = client.post(f"{BASE_URL}/process/{job_id}")
        if response.status_code == 200:
            print(f"✅ Processing started in background")
        else:
            print(f"❌ Processing failed: {response.text}")
            sys.exit(1)
        
        # Step 3: Poll for results
        print("\n⏳ Step 3: Waiting for processing to complete...")
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(2)
            response = client.get(f"{BASE_URL}/result/{job_id}")
            
            if response.status_code == 200:
                result = response.json()
                if result["status"] == "completed":
                    print(f"\n✅ Processing completed in {result['processing_time_ms']:.2f}ms")
                    print("\n" + "="*60)
                    print("📋 FULL RESULT:")
                    print("="*60)
                    
                    # OCR Output
                    if result.get("ocr_output"):
                        print(f"\n📖 OCR OUTPUT:")
                        print(f"   Engine: {result['ocr_output']['engine']}")
                        print(f"   Confidence: {result['ocr_output']['confidence']}")
                        print(f"   Text: {result['ocr_output']['raw_text'][:200]}...")
                    
                    # Post Processing
                    if result.get("post_processing"):
                        pp = result["post_processing"]
                        print(f"\n🧹 POST-PROCESSING:")
                        print(f"   Original length: {pp['original_length']}")
                        print(f"   Cleaned length: {pp['cleaned_length']}")
                        print(f"   Transformations: {pp['transformations_applied']}")
                    
                    # Intermediate Classification
                    if result.get("intermediate_classification"):
                        ic = result["intermediate_classification"]
                        print(f"\n🏷️  INTERMEDIATE CLASSIFICATION:")
                        print(f"   Category: {ic['predicted_category']}")
                        print(f"   Confidence: {ic['confidence']}")
                        print(f"   Method: {ic['method']}")
                        print(f"   Keywords: {ic['matched_keywords']}")
                        print(f"   Reasoning: {ic['reasoning']}")
                    
                    # LLM Classification
                    if result.get("llm_classification"):
                        llm = result["llm_classification"]
                        print(f"\n🤖 LLM CLASSIFICATION:")
                        print(f"   Label: {llm['label']}")
                        print(f"   Confidence: {llm['confidence']}")
                        print(f"   Model: {llm['model']}")
                        print(f"   Tokens: {llm['tokens_used']}")
                        print(f"   Reasoning: {llm['reasoning']}")
                        print(f"   Entities: {llm['structured_entities']}")
                    
                    print("\n" + "="*60)
                    return
                elif result["status"] == "failed":
                    print(f"❌ Processing failed: {result.get('error')}")
                    sys.exit(1)
                else:
                    print(f"   Still {result['status']}... (attempt {attempt + 1}/{max_attempts})")
            else:
                print(f"   Status check failed: {response.text}")
        
        print("\n⚠️  Timeout waiting for results")
        sys.exit(1)

if __name__ == "__main__":
    main()
