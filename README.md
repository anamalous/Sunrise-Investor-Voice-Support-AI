# 🚀 Sunrise AMC: AI Investor Support Pipeline

An RAG (Retrieval-Augmented Generation) pipeline designed for **Sunrise Asset Management Co. Ltd.** This system transcribes investor voice queries, retrieves grounded financial data from an internal FAQ, and generates accurate, cited responses—all while running locally to ensure data sovereignty.

## 🛠️ Setup & Installation

Follow these steps to get the pipeline running on your local machine.

### 1. Prerequisites
* **Python 3.10+**
* **Ollama:** [Download Ollama](https://ollama.com/) and ensure the service is running.
* **Mistral:** Pull the model via terminal:
  ```bash
  ollama pull mistral
  ```

### 2. Environment Setup
Clone the repository and navigate to the project root:
```bash
# Create a virtual environment
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Pipeline
Ensure your input files (`investor_sample.mp3` and `SunriseAMC_FAQ.pdf`) are in the `/input` folder in the project root.
```bash
python main.py
```
*The final output will be printed to the console and saved in `output/final_response.txt`.*

---

## 🏗️ Tech Stack & Architecture

### 1. Voice Pipeline (STT)
*   **Tech:** `faster-whisper` (Model: `base`)
*   **Role:** Converts investor audio into text with word-level timestamps and confidence scores.

### 2. FAQ Ingestor
*   **Tech:** `PyMuPDF` (fitz) & `Regex`
*   **Role:** Extracts text from FAQ PDF. It uses **structural regex** to maintain "Unit of Truth" chunks (keeping Questions and Answers paired together).

### 3. Knowledge Base (Vector DB)
*   **Tech:** `ChromaDB` & `Sentence-Transformers` (`all-MiniLM-L6-v2`)
*   **Role:** Stores FAQ chunks as embeddings. Uses a lightweight 384-dimension model optimized for CPU-based semantic search.

### 4. Hybrid Retriever
*   **Tech:** Custom Python Logic
*   **Role:** Performs a weighted search combining **Semantic Similarity** (intent), **Keyword Matching** (lexical), and **Metadata Filtering** (category alignment).

### 5. Grounded Generator (LLM)
*   **Tech:** `Ollama` / `Mistral 7B`
*   **Role:** Synthesizes the final answer. It is governed by a **Strict System Prompt** that forbids hallucinations and mandates source citations ("Source: Q9").

---

## 📊 Observability & Metrics

To ensure production standards, the system includes:
*   **Latency Benchmarking:** Detailed breakdown of STT vs. RAG processing times.
*   **Context Utilization Score:** A custom metric measuring how much of the retrieved context was actually utilized in the final response.
*   **System Logging:** A persistent log file (`output/system_trace.log`) that tracks every stage of the pipeline and captures errors for debugging.

---

## 📁 Project Structure
```text
├── input/               # Source PDF and Audio files
├── output/              # Final response, logs, and transcripts
├── data/                # ChromaDB storage
├── src/
│   ├── transcriber.py   # Audio processing
│   ├── ingestor.py      # PDF parsing and DB loading
│   ├── retriever.py     # Hybrid search logic
│   ├── generator.py     # LLM prompting and generation
│   ├── evaluator.py     # Quality metrics
│   └── logger.py        # System-wide logging setup
├── main.py              # Orchestrator
├── README.md
├── DECISIONS.md         # Engineering justifications
└── requirements.txt     # Project dependencies
```
