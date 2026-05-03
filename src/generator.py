import ollama
from src.retriever import retrieve_best_chunks

def generate_final_response(query):
    if not query or len(query.strip()) < 5:
        return "System Error: The provided query is too short or empty to process."
    
    try:
        retrieved_results = retrieve_best_chunks(query) # retrieve chunks for context
    
        if not retrieved_results:
            return "I'm sorry, I couldn't find any information in our official FAQ regarding that specific query."

        context_text = ""
        sources = [] # tracks FAQ passed to model
        for idx, result in enumerate(retrieved_results): # format context to send to model
            context_text += f"--- CONTEXT {idx+1} (Source: {result['metadata']['source']}) ---\n"
            context_text += f"{result['text']}\n\n"
            sources.append(result['metadata']['source'])

        system_message = (
            "You are an AI Investor Support Assistant for Sunrise Asset Management Co. Ltd. "
            "Answer the user query based ONLY on the FAQ context below."
            "Used only as much context as is absolutely relevant to the query."
            "If the query asked is beyond KYC, Onboarding, Taxation, SIP, redemption, say the information is not available in the FAQ and say you do not know"
            "Understand the context provided and interpret it in terms of the query asked."
            "Do not blindly copy content provided but rephrase is as an answer tp the query.."
            "Cite the Source (e.g. Source: Q9) for every statement you make. "
            "If the answer isn't there, say you don't know."
            "Do not connect unrelated terms but find the exact terminology needed."
            "Make no external assumptions."
            "Answer only the query and nothing irrelevant beyond it."
            "IF YOU CANNOT ANSWER THE EXACT QUERY ASKED, directly say You Do Not Know."
        )

        prompt = f"USER QUERY: {query}\n\nFAQ CONTEXT:\n{context_text}"

        print(f"--- Generating Answer using sources: {', '.join(sources)} ---")
    
        response = ollama.chat(model='mistral', messages=[
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': prompt},
        ],
        options={'temperature': 0.1}) # minimise assumptions and imagination from model

        answer = response.get('message', {}).get('content', "").strip()
        if not answer:
            return "System Error: The model generated an empty response. Please try rephrasing your query."
        return answer
    except ConnectionError:
        return "Connection Error: Could not reach Ollama. Ensure 'ollama serve' is running in the background."
    except Exception as e:
        return f"Unexpected Error in Generator: {str(e)}"

if __name__ == "__main__":
    #test_query = "If I redeem my units after 14 months, how will my gains be taxed? And will any TDS be deducted?"
    test_query = "What happens if I default on my loan?" # out of scope query
    answer = generate_final_response(test_query)
    print(f"\nFINAL GROUNDED OUTPUT:\n{answer}")