# AI Financial Planning Assistant

An agentic AI financial planning application that analyzes transaction data, performs deterministic financial calculations, and uses LLM-powered agents to generate personalized recommendations and financial reports.

## Features

- CSV transaction ingestion
- Transaction validation and normalization
- Deterministic financial analysis
- Budget, and expense analysis
- LangGraph-based workflow orchestration
- Recommendation Agent
- Report Agent
- Ollama LLM integration
- Streamlit UI
- Financial reports in Markdown
- Basic financial visualizations
- LLM execution logging and timing

## Architecture

```text
CSV
 ↓
Parser
 ↓
Validator
 ↓
Normalizer
 ↓
Financial Analyzer
 ↓
LangGraph
 ├── Recommendation Agent → Ollama
 └── Report Agent → Ollama
 ↓
Streamlit UI

## Command to run the Application
python -m streamlit run ui/app.py

## Build the Application
docker build -t ai-financial-planner .

## Run the application
docker run -p 8501:8501 ai-financial-planner