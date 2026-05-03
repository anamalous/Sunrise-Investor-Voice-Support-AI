def calculate_utility_score(answer, retrieved_chunks):
    # how much of retrieved chunks were actually used
    sources_cited = 0
    for chunk in retrieved_chunks:
        source_id = chunk['metadata']['source'] 
        if source_id in answer:
            sources_cited += 1
    
    total_sources = len(retrieved_chunks)
    utility_ratio = (sources_cited / total_sources) if total_sources > 0 else 0
    return {
        "metric_name": "Context Utilization Score",
        "score": round(utility_ratio, 2),
        "interpretation": f"{sources_cited} of {total_sources} sources used."
    }