
# 🌌 Cosmic Chatbot

**Cosmic Chatbot** is an intelligent, educational chatbot designed to answer space-related questions using the power of LLMs, vector search, and real-time astronomical data. Built with Streamlit and Groq's LLaMA 3 model, it offers a rich, responsive experience for users curious about the universe.

---

## 🚀 Features

* **Natural Language Q\&A** powered by LLaMA 3 (via Groq API)
* **Semantic Topic Matching** using SBERT embeddings
* **Vector Search on arXiv** for relevant scientific paper summaries
* **NASA APOD (Astronomy Picture of the Day)** integration
* **Real-time Solar Activity & Moon Phase Data**
* **Wikipedia Summaries & Images** for context
* **Stylish UI** with space-themed background and font

---

## 🧠 Technologies Used

| Tech                            | Description                             |
| ------------------------------- | --------------------------------------- |
| Streamlit                       | Web UI framework                        |
| Groq LLM                        | LLaMA3-70B for answering questions      |
| LlamaIndex                      | Vector search & document indexing       |
| HuggingFace SentenceTransformer | For topic embedding matching            |
| NASA API                        | APOD image, explanation                 |
| arXiv                           | Scientific paper metadata retrieval     |
| Wikipedia API                   | Contextual knowledge                    |
| Ephem                           | Astronomical calculations (moon phases) |

---

## 🖼️ Screenshots

> *(Add screenshots of the app interface here, e.g. showing an image of a black hole + explanation)*

---

## 🏗️ How It Works

1. **User enters a space-related question**
2. **Topic Matching** via cosine similarity over a list of known astrophysical concepts
3. **Context Gathering:**

   * Wikipedia summary
   * arXiv paper search & vector retrieval
   * NASA & NOAA real-time feeds
4. **Prompt Creation** using all the gathered context
5. **LLM Completion** via Groq API with structured, grounded output

---

## 🛠️ Setup Instructions

### Prerequisites

* Python 3.9+
* Create `.streamlit/secrets.toml` with:

```toml
GROQ_API_KEY = "your-groq-key"
NASA_API_KEY = "your-nasa-api"
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run locally

```bash
streamlit run app.py
```

---

## 📦 `requirements.txt`

```
streamlit
requests
beautifulsoup4
feedparser
arxiv
llama-index
llama-index-llms-groq
sentence-transformers
torch
ephem
matplotlib
numpy
```

---

## ✍️ Author

* Afsaneh [🔗 LinkedIn](www.linkedin.com/in/afsaneh-esm)

---

## 📌 Notes

* If LLM fails to respond, check `response.text` vs `response.message.content`
* Groq's model may be slow or fail silently under load — use fallback model like `llama3-8b-8192`
* Deployment on [Streamlit Cloud](https://share.streamlit.io/) recommended

---

## 📚 License

MIT License

