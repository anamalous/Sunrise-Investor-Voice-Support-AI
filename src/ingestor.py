import os
import re
import fitz
import chromadb
from chromadb.utils import embedding_functions

def ingest_faq(pdf_path, db_path):
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return

    try:
        doc = fitz.open(pdf_path)
        full_text = "\n".join([page.get_text("text") for page in doc])
        doc.close()
        
        if not full_text.strip():
            print("Error: PDF appears to be empty or OCR is required.")
            return
            
    except Exception as e:
        print(f"Error opening PDF: {str(e)}")
        return
    
    section_pattern = r"(?m)^(\d+)\.\s+([A-Z,a-z ]+)" # number. capital / lower case letters
    qa_pattern = r"(Q(\d+)\..+?)(?=Q\d+\.|\d+\.\s+[A-Z]|$)" # Qnumber. text... Q
    parts = re.split(section_pattern, full_text) # get section splits
    
    documents, metadatas, ids = [], [], []

    for i in range(1, len(parts), 3):
        try:
            category = parts[i+1].strip()
            section_content = parts[i+2]
        
            # find all Q&A within this specific section
            qa_matches = re.findall(qa_pattern, section_content, re.DOTALL)
        
            for q_text, q_id in qa_matches:
                full_chunk = f"Category: {category}\n{q_text.strip()}"
                documents.append(full_chunk)
                metadatas.append({
                    "category": category, # used later for category scoring
                    "q_number": int(q_id),
                    "source": f"FAQ Q{q_id}"
                })
                ids.append(f"id_{q_id}")
        except Exception as e:
            print(f"Warning: Skipping a section segment due to error: {e}")
            continue
    if not documents:
        print("Error: No Q&A pairs could be extracted. Check Regex patterns.")
        return

    for doc in documents:
        print(doc)

    try:
        client = chromadb.PersistentClient(path=db_path)
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        collection = client.get_or_create_collection(name="amc_faq", embedding_function=emb_fn)

        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f"--- Successfully Ingested {len(documents)} Q&A pairs ---")
        
    except Exception as e:
        print(f"Database Error: {str(e)}")
    
if __name__ == "__main__":
    ingest_faq("input/SunriseAMC_FAQ.pdf", "data/chroma_db")