# LangGraph AI Agent System

Un sistema multi-agente orchestrato tramite grafi, basato su LangGraph, per task complessi.

## 🎯 Scopo
Coordinare più agenti specializzati che cooperano in un flusso definito da un grafo:
- **Retrieval Agent**: interroga un database vettoriale o direttamente contesto fornito da utente
- **Classification Agent**: etichetta e classifica il contenuto
- **Persona Simulator Agent**: simula comportamenti/risposte di un utente

## 🛠 Tecnologie principali
- **LangGraph** per definire nodi e archi del flusso di esecuzione
- **Google Gemini** (tramite API) come LLM remoto
- **Pydantic** schema e normalizzazione formato dati
- **Python 3.10+**

## 📦 Dipendenze
- `langgraph`
- `pydantic`
- `requests`
- `pytest`

## 🚀 Installazione & Setup
```bash
git clone https://github.com/ZakDeveloperAI/LangGraph_AI_Agent_System.git
cd LangGraph_AI_Agent_System
pip install -r requirements.txt

# Imposta la chiave API per Gemini
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

