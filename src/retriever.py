import chromadb
from chromadb.utils import embedding_functions
import re
from src.parser import advanced_query_parser

def calculate_custom_score(query, doc_text, metadata, semantic_dist, query_categories):
    semantic_score = max(0, 1 - semantic_dist) # 1 - distance = similarity
    
    cat_score = 0 # category score = how much query and chunk match conceptually
    if query_categories:
        doc_cat = metadata.get("category", "")
        if doc_cat in query_categories:
            cat_score += (1 / len(query_categories))

    words = re.findall(r'\w+', query.lower()) # tokenize query
    doc_words = set(re.findall(r'\w+', doc_text.lower())) # tokenize chunk 
    matches = [w for w in words if w in doc_words] # keyword match 
    keyword_score = len(matches) / len(words) if words else 0

    # weighted final Score
    final_score = (0.15 * cat_score) + (0.35 * keyword_score) + (0.5 * semantic_score)
    return final_score

def retrieve_best_chunks(query):
    try:
        client = chromadb.PersistentClient(path="data/chroma_db")
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

        collections = client.list_collections() # has a file been ingested?
        if not any(c.name == "amc_faq" for c in collections):
            print("Error: Vector database collection 'amc_faq' not found. Run ingestor first.")
            return []
    
        collection = client.get_collection(name="amc_faq", embedding_function=emb_fn)
        query_cats = advanced_query_parser(query)

        if collection.count() == 0:
            print("Warning: Vector database is empty.")
            return []
      
        results = collection.query(query_texts=[query], n_results=5) # semantic top 5
        if not results or not results['documents'][0]:
            return []
    
        scored_results = []
        for i in range(len(results['documents'][0])):
            text = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            dist = results['distances'][0][i]
        
            score = calculate_custom_score(query, text, meta, dist, query_cats)
            scored_results.append({
                "text": text,
                "metadata": meta,
                "score": score
            })
    
        scored_results.sort(key=lambda x: x['score'], reverse=True) # custom sort by weight
        return scored_results[:2] # get top 2 results
    
    except Exception as e:
        print(f"Retrieval Error: {str(e)}")
        return []
if __name__ == "__main__":
    test_query = "If I redeem my units after 14 months, how will my gains be taxed? And will any TDS be deducted?"
    res = retrieve_best_chunks(test_query)
    for best in res:
        print(f"Chunk: {best['metadata']['source']}")
        print(f"Score: {best['score']:.4f}")
        print(f"Content Snippet: {best['text'][:100]}...")