import os
import time
from src.evaluator import calculate_utility_score
from src.retriever import retrieve_best_chunks
from src.transcriber import transcribe_audio
from src.generator import generate_final_response
from src.logger import logger

def main():
    start_time = time.time()
    logger.info("--- PIPELINE START ---")

    INPUT_AUDIO = "input/investor_sample.mp3"
    OUTPUT_FILE = "output/final_response.txt"

    if not os.path.exists(INPUT_AUDIO):
        print(f"Error: Missing {INPUT_AUDIO}")
        return

    print("🚀 Starting Sunrise AMC Voice Assistant Pipeline...")
    
    t0 = time.time()
    print("\n[Stage 1/3] Transcribing Audio...")
    transcript_result = transcribe_audio(INPUT_AUDIO, "output")
    t_stt = time.time() - t0 # time for text to speech

    if "error" in transcript_result:
        logger.error(f"Transcription failed: {transcript_result['error']}")
        return

    if transcript_result["warnings"]!=[]:
        for w in transcript_result["warnings"]:
            logger.error(f"Transcription failed: {w}")
        return
    
    user_query = transcript_result['transcript']
    logger.info(f"Query recognized: {user_query}")

    t1 = time.time()
    print("\n[Stage 2 & 3/3] Retrieving Context & Generating Answer...")
    chunks = retrieve_best_chunks(user_query) # for evaluation
    final_answer = generate_final_response(user_query)
    t_rag = time.time() - t1 # time for retrieval

    eval_result = calculate_utility_score(final_answer, chunks)
    logger.info(f"Evaluation: {eval_result['metric_name']} = {eval_result['score']}")
    
    total_time = time.time() - start_time # turn around time

    # advisory disclaimer
    final_answer+="\nMutual Fund investments are subject to market risks. Please read all scheme related documents carefully before investing"

    print("\n" + "="*50)
    print(f"ASSISTANT: {final_answer}")
    print("-" * 50)
    print(f"METRIC: [{eval_result['metric_name']}: {eval_result['score']}]")
    print(f"INSIGHT: {eval_result['interpretation']}")
    print("="*50)

    print(f"\nLATENCY BENCHMARKS:")
    print(f"STT Phase: {t_stt:.2f}s")
    print(f"RAG Phase: {t_rag:.2f}s")
    print(f"Total Turnaround: {total_time:.2f}s")

    with open(OUTPUT_FILE, "w") as f:
        f.write(f"USER QUERY: {user_query}\n\n")
        f.write(f"ASSISTANT RESPONSE:\n{final_answer}")

    print(f"\nDone! Final response saved to {OUTPUT_FILE}")
    print("\n" + "="*50)
    print(final_answer)
    print("="*50)

if __name__ == "__main__":
    main()