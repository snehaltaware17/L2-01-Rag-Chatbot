#DocMind AI – PDF Question Answering using RAG


## Overview
**DocMind AI** is a Retrieval-Augmented Generation (RAG) application that enables users to ask questions about a PDF document using a local Large Language Model (LLM).

The application extracts text from a PDF, divides it into smaller chunks, converts those chunks into vector embeddings, stores them in **ChromaDB**, retrieves the most relevant content for a user's query, and generates context-aware answers using **Ollama**.
This project demonstrates the core concepts of Retrieval-Augmented Generation (RAG), including document ingestion, semantic search, vector databases, and local LLM inference.


**Assignment:** OS3 AI Engineer Technical Evaluation Program  
**Set 2 – L2-01: Retrieval-Augmented Generation (RAG) Chatbot**



# Features
- PDF document ingestion
- Automatic text chunking
- Semantic vector embeddings
- ChromaDB vector database
- Context-aware document retrieval
- Question answering using a local LLM
- Streamlit-based interactive interface
- Persistent vector database
- Fast semantic search



# Tech Stack

| Technology    | Purpose |
|------------   |---------
| Python        | Programming Language 
| Streamlit     | Web Interface 
| LangChain     | RAG Pipeline 
| Ollama        |   Local LLM & Embeddings 
| ChromaDB      | Vector Database 
| PyPDF         | PDF Processing 
| Python-dotenv | Environment Variables 



# Project Structure
LLM/
│
├── app.py
├── data/
│   └── sample.pdf
│
├── chroma_db/
│
├── venv/
│
├── .env
├── requirements.txt
└── README.md



# Prerequisites
- Python 3.10 or above
- Ollama installed locally


Download Ollama:
https://ollama.com


Pull the required models:
ollama pull nomic-embed-text
ollama pull qwen2.5:0.5b



Start Ollama:
ollama serve


# Installation

### Create Virtual Environment
python -m venv venv
### Activate Environment
Windows
	venv\Scripts\activate
Linux/macOS
	source venv/bin/activate




### Install Dependencies
pip install -r requirements.txt



# Configuration
Create a `.env` file in the project root.

```env
# Future environment variables can be added here
```


Place your PDF inside the **data** folder.
data/
    sample.pdf


# Running the Application
Start the Streamlit application.
	streamlit run app.py


The application will open at:
http://localhost:8501




# How It Works

### Step 1 – Document Processing
- Load the PDF using **PyPDFLoader**
- Split the document into smaller chunks using **RecursiveCharacterTextSplitter**
- Generate embeddings using **nomic-embed-text**
- Store embeddings inside **ChromaDB**

### Step 2 – Question Answering
- User enters a question
- The application retrieves the most relevant document chunk
- Retrieved context is passed to the LLM
- The LLM generates an answer based on the retrieved document context
- The answer is displayed in the Streamlit interface

---

# System Architecture

```
                PDF Document
                     │
                     ▼
                 PyPDFLoader
                     │
                     ▼
        RecursiveCharacterTextSplitter
                     │
                     ▼
              Ollama Embeddings
              (nomic-embed-text)
                     │
                     ▼
                  ChromaDB
                     │
             Semantic Retrieval
                     │
User Question ───────┘
                     │
                     ▼
          Ollama LLM (Qwen2.5)
                     │
                     ▼
             Generated Answer


# Sample Questions

- What is Business Intelligence?
- Hi
- What is AI?



# Design Decisions
- **Ollama** is used to perform all inference locally, helping keep document processing on the local machine.
- **ChromaDB** provides persistent vector storage and integrates well with LangChain.
- **RecursiveCharacterTextSplitter** improves retrieval by dividing the document into overlapping chunks.
- **Semantic search** retrieves the document content that is most relevant to the user's query before generating a response.
- **Streamlit** provides a lightweight and interactive user interface.


# Future Enhancements
- Support multiple PDF uploads
- Display source page numbers
- Conversational chat history
- Retrieve multiple relevant chunks for improved answers
- PDF summarization
- Streaming responses
- Export answers
- User authentication


# Requirements
streamlit==1.41.1
langchain==0.3.14
langchain-community==0.3.14
langchain-text-splitters==0.3.4
langchain-ollama==0.2.3
chromadb==0.5.23
pypdf==5.1.0
python-dotenv==1.0.1




# Author
**Snehal**
M.Tech Computer Engineering
OS3 AI Engineer Technical Evaluation Program
Set 2 – L2-01: Retrieval-Augmented Generation (RAG) Chatbot