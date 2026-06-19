# 🤖 Research Agent

An AI-powered Research Agent built using FastAPI, LangGraph, MongoDB Atlas, Tavily Search, Groq LLM, JWT Authentication, and Streamlit.

The system automatically researches a topic from the web, gathers relevant information, generates an AI-powered summary, and stores research history for authenticated users.

---

## 🚀 Features

### User Authentication

* User Signup
* User Login
* JWT Token Authentication
* Argon2 Password Hashing
* Protected API Endpoints

### AI Research Workflow

* Topic-based research
* Web search using Tavily
* AI summarization using Groq LLM
* Multi-step workflow using LangGraph
* Execution time tracking

### Database Integration

* MongoDB Atlas
* User Management
* Research History Storage
* Research Logs

### Frontend

* Streamlit User Interface
* Login and Signup Forms
* Research Dashboard
* Session Management

---

## 🏗️ System Architecture

```text
User
  │
  ▼
Streamlit Frontend
  │
  ▼
FastAPI Backend
  │
  ├── JWT Authentication
  ├── User Management
  ├── Research Endpoint
  │
  ▼
LangGraph Workflow
  │
  ├── Tavily Search
  └── Groq LLM
  │
  ▼
MongoDB Atlas
```

---

## 🛠️ Tech Stack

### Backend

* FastAPI
* Python
* LangGraph
* Pydantic

### AI & Research

* Tavily Search API
* Groq LLM
* Llama 3.3 70B

### Database

* MongoDB Atlas
* Motor Async Driver

### Authentication

* JWT
* Argon2 Password Hashing

### Frontend

* Streamlit

---

## 📂 Project Structure

```text
Research_Agent/

├── app/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── schemas.py
│   ├── workflow.py
│   └── routes/
│
├── frontend/
│   └── streamlit_app.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Ammad12345390/Reasearch_Agent_1.git
cd Reasearch_Agent_1
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
MONGODB_URL=your_mongodb_connection_string

DATABASE_NAME=research_agent_db

JWT_SECRET_KEY=your_secret_key

TAVILY_API_KEY=your_tavily_api_key

GROQ_API_KEY=your_groq_api_key
```

---

## ▶️ Run FastAPI Server

```bash
uvicorn app.main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## ▶️ Run Streamlit Frontend

```bash
streamlit run frontend.py
```

---

## 🔑 Authentication Flow

1. User signs up.
2. Password is hashed using Argon2.
3. User logs in.
4. FastAPI generates JWT Access Token.
5. Streamlit stores the token.
6. Protected endpoints validate the token before processing requests.

---

## 📌 API Endpoints

### Health Check

```http
GET /
```

### Signup

```http
POST /signup
```

### Login

```http
POST /login
```

### Generate Research Summary

```http
POST /generate-summary
```

---

## 🧠 LangGraph Workflow

### Step 1: Research Node

* Searches the web using Tavily
* Collects relevant information

### Step 2: Summarizer Node

* Sends gathered information to Groq LLM
* Generates concise research summary

### Step 3: Logging Node

* Saves research history to MongoDB Atlas

---

## 📊 Example Response

```json
{
  "summary": "Artificial Intelligence is transforming healthcare, education, and automation by enabling machines to perform tasks that typically require human intelligence.",
  "execution_time": 4.23
}
```

---

## 🎯 Future Improvements

* Research History Dashboard
* PDF Export
* Multi-Agent Workflow
* Email Reports
* Research Citations
* Role-Based Access Control
* Docker Deployment
* Cloud Deployment

---

## 👨‍💻 Author

Ammad Kabir

AI Engineer | FastAPI Developer | Agentic AI Enthusiast

GitHub:
https://github.com/Ammad12345390
