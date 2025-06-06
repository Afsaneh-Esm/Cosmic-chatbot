# ─────────────── 1. Imports ───────────────
import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import feedparser
import arxiv
import re
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
os.environ["GROQ_API_KEY"] = "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"
NASA_API_KEY = "rD8cgucyU9Rgcn1iTaOeh7mo1CPd6oN4CYThCdjg"

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

def extract_topic(query):
    import re

    def normalize(text):
        text = text.lower()
        text = re.sub(r"[?.,!]", "", text)
        return text

    def lemmatize(word):
        if word.endswith("ies"):
            return word[:-3] + "y"
        elif word.endswith("es"):
            return word[:-2]
        elif word.endswith("s") and not word.endswith("ss"):
            return word[:-1]
        return word

    query = normalize(query)
    words = query.split()
    normalized_query = " ".join([lemmatize(w) for w in words])

    known_topics = [
        "black hole", "white dwarf", "milky way", "solar system", "event horizon",
        "event horizon telescope", "dark matter", "neutron star", "cosmic microwave background",
        "large magellanic cloud", "small magellanic cloud", "international space station",
        "james webb space telescope", "hubble space telescope", "alpha centauri", "proxima centauri",
        "supernova", "galactic center", "gravitational wave", "red giant", "brown dwarf",
        "star formation", "planetary nebula", "accretion disk", "quasar", "blazar",
        "pulsar", "x-ray binary", "gamma ray burst", "solar flare", "aurora borealis",
        "sunspot", "coronal mass ejection", "cosmic ray", "heliosphere", "exoplanet",
        "hot jupiter", "super-earth", "ice giant", "gas giant", "terrestrial planet",
        "planet nine", "oort cloud", "kuiper belt", "asteroid belt", "dwarf planet",
        "pluto", "ceres", "eris", "makemake", "haumea", "uranus", "neptune",
        "saturn", "jupiter", "mars", "venus", "mercury", "earth", "moon",
        "apollo program", "voyager 1", "voyager 2", "new horizons", "space shuttle",
        "spacex", "falcon 9", "starship", "rosetta mission", "kepler mission",
        "tess mission", "gaia mission", "chandra x-ray observatory", "spitzer space telescope",
        "soho", "iss", "nasa", "esa", "blue origin", "rocket lab",
        "starlink", "space debris", "space tourism", "mars rover", "perseverance",
        "curiosity", "ingenuity", "insight lander", "space weather", "planetary defense",
        "double asteroid redirect test"
    ]

    for topic in sorted(known_topics, key=len, reverse=True):
        topic_words = [lemmatize(w) for w in topic.split()]
        normalized_topic = " ".join(topic_words)
        pattern = r"" + re.escape(normalized_topic) + r""
        if re.search(pattern, normalized_query):
            return topic

    return "space"

def get_wikipedia_summary(topic):
    try:
        topic = topic.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("extract", "")
        return ""
    except:
        return ""

def get_duckduckgo_summary(topic):
    try:
        url = f"https://api.duckduckgo.com/?q={topic}&format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            abstract = data.get("Abstract")
            return abstract if abstract else ""
        return ""
    except:
        return ""

def get_fallback_summary(query):
    topic = extract_topic(query)
    wiki = get_wikipedia_summary(topic)
    if wiki:
        return wiki
    duck = get_duckduckgo_summary(topic)
    if duck:
        return duck
    return "No fallback summary available."

def search_arxiv(query, max_results=10):
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending)
        return [f"{res.title}\n\n{res.summary}" for res in search.results()]
    except:
        return []

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
    with st.spinner("🔄 Retrieving answer from the cosmos..."):
        topic = extract_topic(query)
        wiki_context = get_fallback_summary(query)
        live_context = get_solar_activity() + "\n" + get_next_full_moon()

        if wiki_context:
            final_context = wiki_context + "\n\n" + live_context
        else:
            arxiv_texts = search_arxiv(query)
            docs = [Document(text=t) for t in arxiv_texts]
            index = VectorStoreIndex.from_documents(docs)
            nodes = index.as_retriever().retrieve(query)
            arxiv_context = "\n\n".join([n.get_content()[:500] for n in nodes])
            final_context = live_context + "\n\n" + arxiv_context

        prompt = f"""
You are a cosmic assistant that must answer space-related questions clearly and accurately based only on the following context.
If the context does not contain the answer, say \"I don't know based on available data.\"

Context:
{final_context}

Question: {query}
Answer:
"""
        response = llm.complete(prompt=prompt)

        st.subheader("🔊 Topic Extracted:")
        st.code(topic)

        st.subheader("🔊 Wikipedia or DuckDuckGo Summary Used:")
        st.code(wiki_context, language="markdown")

        st.subheader("🛋️ Final Context Sent to LLM:")
        st.code(final_context[:2000], language="markdown")

        st.subheader("💬 Cosmic Answer")
        st.markdown(response.text)
else:
    st.info("Enter a question about the cosmos to begin your journey! 🚀")
