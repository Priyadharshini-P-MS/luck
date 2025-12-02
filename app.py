import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Witness Archive", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/ICE_Chicago_REAL_dataset.csv")

df = load_data()
st.title("📚 Witness Archive – ICE Narratives in Chicago")

# Sidebar Filters
sources = st.sidebar.multiselect("Source", df["Source"].unique(), default=df["Source"].unique())
emotions = st.sidebar.multiselect("Emotion", df["Emotion Label"].unique(), default=df["Emotion Label"].unique())
themes = st.sidebar.multiselect("Theme", df["Thematic Label"].unique(), default=df["Thematic Label"].unique())

# Filtered Data
filtered = df[
    df["Source"].isin(sources) &
    df["Emotion Label"].isin(emotions) &
    df["Thematic Label"].isin(themes)
]

# Charts
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(px.histogram(filtered, x="Emotion Label", title="Emotion Distribution"), use_container_width=True)
with col2:
    st.plotly_chart(px.histogram(filtered, x="Thematic Label", title="Theme Distribution"), use_container_width=True)

# Table Viewer
st.markdown("### Narrative Snippets")
for _, row in filtered.iterrows():
    st.markdown(f"**{row['Title']}** ({row['Source']}, {row['Publication Date']})  
"
                f"*Emotion:* {row['Emotion Label']} | *Theme:* {row['Thematic Label']}  
"
                f"[Read More]({row['URL']})  
"
                f"> {row['Summary']}")
    st.markdown("---")
