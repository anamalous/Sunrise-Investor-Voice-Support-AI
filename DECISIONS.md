# DECISIONS and TRADE-OFFS

### 1. Model Selection
* **LLM: Mistral (7B) via Ollama**
    *   **Reasoning:** While I initially considered Llama 3, I ultimately selected **Mistral 7B** for final deployment to optimize for **CPU-based inference speed**. Mistral’s architecture provides a higher throughput-to-parameter ratio, making it more responsive on hardware without dedicated GPU acceleration.
    *   **Precision:** Mistral's instruction-following capabilities remain robust for RAG tasks, ensuring it stays strictly within the provided FAQ context without drifting into general financial advice.
    *   **Reliability:** During the development sprint, Mistral demonstrated higher stability in local pull/load times, ensuring the "single command" execution requirement was met consistently under varying network conditions.
*   **Embeddings: `all-MiniLM-L6-v2` (Sentence-Transformers)**
    *   **Reasoning:** This model is highly optimized for CPU-only environments. With a 384-dimension vector space, it provides high-speed retrieval without the overhead of larger models, which is ideal for a 10-item FAQ knowledge base.

### 2. Chunking Strategy
*   **Strategy: Structural Regex-Based Q&A Splitting**
    *   **Why I avoided Fixed-Size/Overlap?** Traditional recursive chunking (based on chunk lengths and consecutive overlap) risks splitting a financial rule or connected components of an answer mid-sentence, leading to loss of context.
    *   **Logic:** I implemented a "Structure-Aware" parser that uses Python’s re module to identify the document's inherent schema. Specifically, the logic uses regex patterns to detect Section Headers (e.g., 1. KYC) and Q&A blocks (e.g., Q1. ... Answer ...), ensuring each logical unit is kept whole.
    *   **The "Unit of Truth":** Each chunk consists of one full Question and its corresponding Answer. This ensures that the embedding vector represents a complete logical concept, resulting in 100% contextual integrity.

### 3. Retrieval Methodology
*   **Hybrid Weighted Scoring:** To ensure maximum accuracy, I moved away from "Naive RAG" to a weighted heuristic:
    *   **Semantic Score (50%):** Captures intent (e.g., matching "14 months" to "Long Term").
    *   **Lexical/Keyword Score (35%):** Prioritizes specific financial terms like "TDS" or "SIP."
    *   **Categorical Match (15%):** Used metadata filtering to prioritize the correct section in the document (Tax, KYC, etc.).

### 4. Trade-offs Made
*   **Inference Speed vs. Architectural Complexity:** I prioritized a **Direct-to-Generation** flow over an orchestrated "Agentic" framework. While using multiple agents or function-calling loops can provide more nuanced reasoning, it would have introduced prohibitive latency on CPU hardware. By feeding the retrieval context directly into Mistral 7B, the system provides a faster, more reliable "grounded" response for the investor.
*   **Mistral 7B for CPU Optimization:** I selected Mistral 7B specifically for its efficiency in non-GPU environments. While larger models (like Llama 3 70B) offer higher reasoning capabilities, they are unusable on standard hardware. Mistral provides the best "intelligence-per-second" ratio for local deployment.
*   **Local Data Sovereignty vs. API Latency:** Opting for a local Ollama setup increases the initial load time and inference duration compared to using a cloud-based API like Groq or OpenAI. However, this trade-off was made to ensure **data privacy and sovereignty**, keeping sensitive AMC financial data within the local infrastructure rather than sending it to external servers.

### 5. Production Readiness
If this system were to be deployed at Sunrise AMC for thousands of investors, I would implement the following:
1.  **Speech Enhancement:** Add a noise-reduction preprocessing layer (like `RNNoise`) to handle poor-quality investor audio recordings.
2.  **Reranking Layer:** Implement a Cross-Encoder (like BGE-Reranker) after the initial retrieval to refine the top results before sending them to the LLM.
3.  **Human-in-the-Loop:** Add a confidence threshold. If the retrieval score is below 0.4, the system should flag the query for a manual support agent rather than risking a hallucinated answer.
4.  **Evaluation Framework:** Use **Ragas** or **TruLens** to quantitatively measure Faithfulness and Answer Relevance over a larger test dataset.
5.  **Streaming UI:** Transition from a CLI to a FastAPI-based backend to provide real-time transcription and "typing" feedback to the investor.

### 6. Scalability & Bottlenecks
*   **CPU Dependence:** Relying on CPU for model inference leads to linear scaling issues. As the number of concurrent users increases, the **130s+ RAG latency** would grow exponentially, resulting in a poor user experience. 
*   **Sequential Pipeline Execution:** The current "Stall-and-Wait" flow (STT must finish before RAG starts) creates a significant "silent period" for the user.
*   **Singular ChromaDB Point of Failure:** A local, file-based vector database cannot handle distributed access or high-concurrency write operations. It also lacks built-in redundancy.
*   **Model Intelligence Constraints:** While Mistral 7B is highly efficient, smaller local models are more prone to "Instruction Drift" compared to larger 70B+ models or Frontier APIs when handling highly complex, multi-part financial queries.