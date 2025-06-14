# ─────────────── 1. Imports ───────────────
import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
import feedparser
import arxiv
import re
import numpy as np
import matplotlib.pyplot as plt
import ephem
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.llms.groq import Groq
from sentence_transformers import SentenceTransformer, util

# ─────────────── Custom Embedding Class ───────────────
class MyEmbedding:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.model.encode(t).tolist() for t in texts]

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

embed_model = MyEmbedding()
Settings.embed_model = embed_model
llm = Groq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
Settings.llm = llm
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# ─────────────── 4. Helper Functions ───────────────
# (همون توابع get_apod_image، get_nasa_news، get_solar_activity، get_next_full_moon و بقیه مثل قبل هستن)

# برای خلاصه‌سازی در اینجا فقط core بخش‌ها رو گذاشتم. اگه خواستی نسخه کامل آپلودی بفرستم.

# ─────────────── 5. Streamlit App Logic ───────────────
# (همون قسمت‌های input، topic match، ساخت context، گرفتن پاسخ و نمایش هم تغییری نکرده.)

# فقط تغییری که لازمه بدی مربوط به کلاس MyEmbedding بود که دادم بالا 👆
