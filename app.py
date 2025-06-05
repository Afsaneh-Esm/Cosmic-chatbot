# ─────────────── 1. Imports ───────────────
import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import feedparser
import arxiv
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

# ─────────────── 2. Page config and CSS ───────────────
st.set_page_config(page_title="🌌 Cosmic Chatbot", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://apod.nasa.gov/apod/image/2305/MWandAurora_Odegard_960.jpg");
    background-size: cover;
    background-position: center;
}
html, body, [class*="css"] {
    font-family: 'Orbitron', sans-serif;
}
</style>
<link href="https://fonts.googleapis.com/css2?family=Orbitron&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ─────────────── 3. API Keys and LLM ───────────────
os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY"
NASA_API_KEY = "YOUR_NASA_API_KEY"

embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2", device="cpu")
Settings.embed_model = embed_model
llm = Groq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
Settings.llm = llm

# ─────────────── 4. Helper Functions ───────────────

def get_apod_image():
    try:
        res = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}")
        data = res.json()
        return data.get("title", ""), data.get("url", ""), data.get("explanation", "")
    except:
        return "", "", "Could not load image."

def get_nasa_news():
    try:
        feed_url = "https://www.nasa.gov/news-release/rss"
        feed = feedparser.parse(feed_url)
        return [(entry.title, entry.link) for entry in feed.entries[:5]]
    except:
        return [("Could not fetch NASA news.", "#")]

def get_solar_activity():
    try:
        res = requests.get("https://services.swpc.noaa.gov/json/flares.json")
        data = res.json()
        if data:
            flare = data[0]
            return f"☀️ Solar flare: class {flare['classType']} at {flare['beginTime']}"
    except:
        return "No solar activity data."

def get_next_full_moon():
    try:
        res = requests.get("https://www.timeanddate.com/moon/phases/")
        soup = BeautifulSoup(res.text, "html.parser")
        row = soup.find("table", class_="tb-sm").find_all("tr")[1]
        return "🌕 Next full moon: " + row.get_text(" ", strip=True)
    except:
        return "Lunar data unavailable."

def search_arxiv(query, max_results=4):
    search = arxiv.Search(query=query, max_results=max_results)
    return [f"{res.title}\n\n{res.summary}" for res in search.results()]

# ─────────────── 5. Streamlit App ───────────────

st.title("🌌 Ask the Cosmos")
st.markdown("Type a space-related question (e.g., *When is the next full moon?* or *What is Jupiter?*)")

query = st.text_input("Ask your question about the universe:")

# ───── NASA APOD Section ─────
st.subheader("📸 NASA Astronomy Picture of the Day")
title, img_url, desc = get_apod_image()
if img_url:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(img_url, caption=title, use_container_width=True)
    st.markdown(f"<p style='text-align: center;'>{desc}</p>", unsafe_allow_html=True)

# ───── NASA News Section ─────
st.subheader("📰 Latest NASA News")
for title, link in get_nasa_news():
    st.markdown(f"- [{title}]({link})")

# ───── Sidebar Live Info ─────
st.sidebar.header("🔭 Solar & Lunar Updates")
st.sidebar.markdown(get_solar_activity())
st.sidebar.markdown(get_next_full_moon())

# ───── Chat Section ─────
if query:
    with st.spinner("🔄 Searching arXiv and preparing context..."):
        arxiv_texts = search_arxiv(query)
        docs = [Document(text=t) for t in arxiv_texts]

        index = VectorStoreIndex.from_documents(docs)
        nodes = index.as_retriever().retrieve(query)
        context = "\n\n".join([n.get_content()[:500] for n in nodes])

        live_context = get_solar_activity() + "\n" + get_next_full_moon()
        final_context = live_context + "\n\n" + context

        prompt = f"""
You're a cosmic assistant. Use the following context to answer clearly and accurately.

{final_context}

Q: {query}
A:"""

        response = llm.complete(prompt=prompt)
        st.subheader("💬 Cosmic Answer")
        st.markdown(response.text)
else:
    st.info("Enter a question about the cosmos to begin your journey! 🚀")
