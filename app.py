import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Page config ----------
st.set_page_config(
    page_title="Witness Archive: ICE Raids in Chicago",
    page_icon="📚",
    layout="wide",
)

# ---------- Load data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("ICE_Chicago_REAL_dataset.csv")
    if "Publication Date" in df.columns:
        df["Publication Date"] = pd.to_datetime(df["Publication Date"], errors="coerce")
    return df

df = load_data()

# ---------- Title ----------
st.title("Witness Archive: Chicago ICE Enforcement")
st.write(
    "Simple interactive dashboard to explore testimonies, emotions, themes, and timeline "
    "from the ICE raids corpus."
)

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

# Emotion filter
if "Emotion" in df.columns:
    emotions = sorted(df["Emotion"].dropna().unique())
    selected_emotions = st.sidebar.multiselect(
        "Emotion", options=emotions, default=emotions
    )
else:
    selected_emotions = None

# Theme filter
if "Theme" in df.columns:
    themes = sorted(df["Theme"].dropna().unique())
    selected_themes = st.sidebar.multiselect(
        "Theme", options=themes, default=themes
    )
else:
    selected_themes = None

# Date filter
if "Publication Date" in df.columns:
    min_date = df["Publication Date"].min()
    max_date = df["Publication Date"].max()
    if pd.notna(min_date) and pd.notna(max_date):
        start_date, end_date = st.sidebar.date_input(
            "Publication date range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
    else:
        start_date, end_date = None, None
else:
    start_date, end_date = None, None

# ---------- Apply filters ----------
filtered_df = df.copy()

if selected_emotions:
    filtered_df = filtered_df[filtered_df["Emotion"].isin(selected_emotions)]

if selected_themes:
    filtered_df = filtered_df[filtered_df["Theme"].isin(selected_themes)]

if (
    start_date is not None
    and end_date is not None
    and "Publication Date" in filtered_df.columns
):
    mask = (filtered_df["Publication Date"].dt.date >= start_date) & (
        filtered_df["Publication Date"].dt.date <= end_date
    )
    filtered_df = filtered_df[mask]

# ---------- Overview ----------
st.subheader("Overview")
c1, c2 = st.columns(2)
c1.metric("Total rows", len(df))
c2.metric("Filtered rows", len(filtered_df))

st.markdown("---")

# ---------- Charts ----------
if not filtered_df.empty and "Emotion" in filtered_df.columns:
    emotion_counts = filtered_df["Emotion"].value_counts().reset_index()
    emotion_counts.columns = ["Emo]()_
