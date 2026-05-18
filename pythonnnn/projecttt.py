import streamlit as st
import pandas as pd
import plotly.express as px
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from collections import Counter
import re

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Azure AI News Analyzer",
    page_icon="🧠",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .main {
        background-color: #0f172a;
        color: white;
    }

    .stTextArea textarea {
        background-color: #1e293b;
        color: white;
        border-radius: 10px;
    }

    .stTextInput input {
        background-color: #1e293b;
        color: white;
    }

    .stButton button {
        background: linear-gradient(90deg,#2563eb,#7c3aed);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }

    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0,0,0,0.3);
    }

    .title {
        text-align: center;
        font-size: 50px;
        font-weight: bold;
        background: linear-gradient(90deg,#38bdf8,#8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================

st.markdown('<div class="title">Azure AI News Analyzer</div>', unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙ Azure Configuration")

endpoint = st.sidebar.text_input("Azure Endpoint")
key = st.sidebar.text_input("Azure Key", type="password")

# =========================================================
# CREATE CLIENT
# =========================================================

def authenticate_client():
    credential = AzureKeyCredential(key)
    client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=credential
    )
    return client

# =========================================================
# INPUT AREA
# =========================================================

st.subheader("📰 Enter News Article")

news_text = st.text_area(
    "Paste news article here",
    height=300,
    placeholder="Paste large news content here..."
)

uploaded_file = st.file_uploader(
    "Or Upload TXT File",
    type=["txt"]
)

if uploaded_file is not None:
    news_text = uploaded_file.read().decode("utf-8")

# =========================================================
# ANALYSIS FUNCTION
# =========================================================

def analyze_news(client, text):

    result = {}

    # Language Detection
    language = client.detect_language(documents=[text])[0]
    result['language'] = language.primary_language.name

    # Sentiment Analysis
    sentiment = client.analyze_sentiment(documents=[text])[0]
    result['sentiment'] = sentiment.sentiment
    result['positive_score'] = sentiment.confidence_scores.positive
    result['neutral_score'] = sentiment.confidence_scores.neutral
    result['negative_score'] = sentiment.confidence_scores.negative

    # Key Phrase Extraction
    key_phrases = client.extract_key_phrases(documents=[text])[0]
    result['key_phrases'] = key_phrases.key_phrases

    # Entity Recognition
    entities = client.recognize_entities(documents=[text])[0]

    persons = []
    organizations = []
    locations = []
    dates = []

    for entity in entities.entities:

        if entity.category == "Person":
            persons.append(entity.text)

        elif entity.category == "Organization":
            organizations.append(entity.text)

        elif entity.category in ["Location", "Address"]:
            locations.append(entity.text)

        elif entity.category in ["DateTime"]:
            dates.append(entity.text)

    result['persons'] = list(set(persons))
    result['organizations'] = list(set(organizations))
    result['locations'] = list(set(locations))
    result['dates'] = list(set(dates))

    # Categorization Logic
    categories = {
        'Politics': ['government', 'election', 'minister', 'parliament'],
        'Technology': ['ai', 'software', 'microsoft', 'google', 'technology'],
        'Sports': ['match', 'football', 'cricket', 'tournament'],
        'Business': ['market', 'company', 'stock', 'finance'],
        'Health': ['hospital', 'health', 'disease', 'medical']
    }

    detected_category = "General"

    lower_text = text.lower()

    for category, keywords in categories.items():
        if any(word in lower_text for word in keywords):
            detected_category = category
            break

    result['category'] = detected_category

    return result

# =========================================================
# RUN ANALYSIS
# =========================================================

if st.button("🚀 Analyze News"):

    if not endpoint or not key:
        st.error("Please enter Azure Endpoint and Key")

    elif not news_text:
        st.error("Please enter news article")

    else:

        try:
            client = authenticate_client()

            with st.spinner("Analyzing article using Azure AI..."):
                result = analyze_news(client, news_text)

            st.success("Analysis Completed Successfully")

            st.markdown("---")

            # =========================================================
            # DASHBOARD METRICS
            # =========================================================

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Language", result['language'])

            with col2:
                st.metric("Category", result['category'])

            with col3:
                st.metric("Sentiment", result['sentiment'])

            with col4:
                st.metric("Key Phrases", len(result['key_phrases']))

            st.markdown("---")

            # =========================================================
            # ENTITY EXTRACTION
            # =========================================================

            c1, c2 = st.columns(2)

            with c1:
                st.subheader("👤 Persons")
                st.write(result['persons'])

                st.subheader("🏢 Organizations")
                st.write(result['organizations'])

            with c2:
                st.subheader("🌍 Locations")
                st.write(result['locations'])

                st.subheader("📅 Important Dates")
                st.write(result['dates'])

            st.markdown("---")

            # =========================================================
            # KEY PHRASES
            # =========================================================

            st.subheader("🔑 Key Phrases")

            phrase_df = pd.DataFrame({
                'Key Phrase': result['key_phrases']
            })

            st.dataframe(phrase_df, use_container_width=True)

            # =========================================================
            # SENTIMENT CHART
            # =========================================================

            st.subheader("📊 Sentiment Analysis")

            sentiment_df = pd.DataFrame({
                'Sentiment': ['Positive', 'Neutral', 'Negative'],
                'Score': [
                    result['positive_score'],
                    result['neutral_score'],
                    result['negative_score']
                ]
            })

            fig = px.pie(
                sentiment_df,
                names='Sentiment',
                values='Score',
                hole=0.5,
                title='Sentiment Distribution'
            )

            st.plotly_chart(fig, use_container_width=True)

            # =========================================================
            # ENTITY FREQUENCY
            # =========================================================

            st.subheader("📈 Entity Frequency")

            all_entities = (
                result['persons'] +
                result['organizations'] +
                result['locations']
            )

            if len(all_entities) > 0:

                freq = Counter(all_entities)

                freq_df = pd.DataFrame({
                    'Entity': list(freq.keys()),
                    'Count': list(freq.values())
                })

                bar_fig = px.bar(
                    freq_df,
                    x='Entity',
                    y='Count',
                    title='Top Extracted Entities'
                )

                st.plotly_chart(bar_fig, use_container_width=True)

            # =========================================================
            # ARTICLE SUMMARY
            # =========================================================

            st.subheader("📝 Article Summary")

            sentences = re.split(r'(?<=[.!?]) +', news_text)
            summary = ' '.join(sentences[:5])

            st.info(summary)

        except Exception as e:
            st.error(f"Error: {str(e)}")