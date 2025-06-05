import streamlit as st
st.set_page_config(page_title="🌌 Cosmic Chatbot", layout="wide")
import os
import requests
from bs4 import BeautifulSoup
import feedparser
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq


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


# Helper Functions
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
        news_items = []
        for entry in feed.entries[:5]:
            news_items.append((entry.title, entry.link))
        return news_items
    except Exception as e:
        print("Error fetching NASA news:", e)
        return [("Could not fetch news.", "#")]

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

# API keys
os.environ["GROQ_API_KEY"] = "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"
NASA_API_KEY = "rD8cgucyU9Rgcn1iTaOeh7mo1CPd6oN4CYThCdjg"

# LLM & Embeddings
embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2", device="cpu")
Settings.embed_model = embed_model
llm = Groq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
Settings.llm = llm

# Load Index
storage_context = StorageContext.from_defaults(persist_dir="storage")
index = load_index_from_storage(storage_context)

# UI Layout

st.title("🌌 Ask the Cosmos")
st.markdown("Type a space-related question (e.g., *When is the next full moon?* or *What is a solar flare?*)")

query = st.text_input("Your cosmic question:")

# NASA APOD
st.subheader("📸 NASA Astronomy Picture of the Day")
title, img_url, desc = get_apod_image()
if img_url:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(img_url, caption=title, use_container_width=True)
    st.markdown(f"<p style='text-align: center;'>{desc}</p>", unsafe_allow_html=True)

# NASA News
st.subheader("📰 Latest NASA News")
for title, link in get_latest_nasa_news_rss():
    st.markdown(f"- [{title}]({link})")

# Sidebar Info
st.sidebar.header("🔭 Solar & Lunar Updates")
st.sidebar.markdown(get_solar_activity())
st.sidebar.markdown(get_next_full_moon())

# Answer from LLM
if query:
    with st.spinner("✨ Scanning the stars..."):
        nodes = index.as_retriever().retrieve(query)
        context = "\n\n".join([n.get_content()[:300] for n in nodes])
        live = get_solar_activity() + "\n\n" + get_next_full_moon()
        final_context = live + "\n\n" + context

        prompt = f"""
You're a helpful and curious space assistant. Use the following context to answer the user's question clearly and accurately.

{final_context}

Q: {query}
A:"""

        response = llm.complete(prompt=prompt)
        st.subheader("💬 Cosmic Answer")
        st.markdown(response.text)
else:
    st.info("Please enter a question to explore the cosmos! 🪐")
