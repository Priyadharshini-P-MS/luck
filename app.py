import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit page settings
st.set_page_config(
    page_title="Witness Archive: ICE Raids in Chicago",
    layout="wide",
)

# ---------- Load Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("ICE_Chicago_REAL_dataset.csv")
    # Convert date column if exists
    if "Publication Date" in df.columns:
        df["Publication Date"] = pd.to_datetime(df["Publication Date"], errors="coerce")
    return df

df = load_data()

st.title("Witness Archive: Public Testimonies of ICE Enforcement in Chicago")
st.write(
    "Explore testimonies, emotions, themes, and sources from the ICE raids dataset."
)

# ---------- Sidebar Filters ----------
st.sidebar.header("Filters")

# Emotion filter
if "Emotion" in df.columns:
    emotions = sorted(df["Emotion"].dropna().unique())
    selected_emotions = st.sidebar.multiselect(
        "Emotion", emotions, default=emotions
    )
else:
    selected_emotions = None

# Theme filter
if "Theme" in df.columns:
    themes = sorted(df["Theme"].dropna().unique())
    selected_themes = st.sidebar.multiselect(
        "Theme", themes, default=themes
    )
else:
    selected_themes = None

# Source filter
if "Source" in df.columns:
    sources = sorted(df["Source"].dropna().unique())
    selected_sources = st.sidebar.multiselect(
        "Source", sources, default=sources
    )
else:
    selected_sources = None

# Date range filter
if "Publication Date" in df.columns:
    min_date = df["Publication Date"].min()
    max_date = df["Publication Date"].max()
    if pd.notna(min_date) and pd.notna(max_date):
        start_date, end_date = st.sidebar.date_input(
            "Publication Date Range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
    else:
        start_date, end_date = None, None
else:
    start_date, end_date = None, None

# ---------- Apply Filters ----------
filtered_df = df.copy()

if selected_emotions:
    filtered_df = filtered_df[filtered_df["Emotion"].isin(selected_emotions)]

if selected_themes:
    filtered_df = filtered_df[filtered_df["Theme"].isin(selected_themes)]

if selected_sources:
    filtered_df = filtered_df[filtered_df["Source"].isin(selected_sources)]

if (
    start_date is not None
    and end_date is not None
    and "Publication Date" in filtered_df.columns
):
    mask = (
        filtered_df["Publication Date"].dt.date >= start_date
    ) & (
        filtered_df["Publication Date"].dt.date <= end_date
    )
    filtered_df = filtered_df[mask]

# ---------- Overview Metrics ----------
st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)
col1.metric("Total Testimonies", len(df))
col2.metric("After Filters", len(filtered_df))
if "Source" in df.columns:
    col3.metric("Unique Sources", df["Source"].nunique())
else:
    col3.metric("Unique Sources", "N/A")

st.markdown("---")

# ---------- Charts ----------
chart_cols = st.columns(2)

# Emotion chart
with chart_cols[0]:
    if "Emotion" in filtered_df.columns and not filtered_df.empty:
        emotion_counts = (
            filtered_df["Emotion"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Emotion", "Emotion": "Count"})
        )
        fig = px.bar(
            emotion_counts,
            x="Emotion",
            y="Count",
            title="Emotion Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

# Theme chart
with chart_cols[1]:
    if "Theme" in filtered_df.columns and not filtered_df.empty:
        theme_counts = (
            filtered_df["Theme"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Theme", "Theme": "Count"})
        )
        fig = px.bar(
            theme_counts,
            x="Theme",
            y="Count",
            title="Theme Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ---------- Table Viewer ----------
st.subheader("Filtered Testimonies")

show_cols = [
    col for col in
    ["Title", "Emotion", "Theme", "Source", "Publication Date", "URL"]
    if col in filtered_df.columns
]

if not filtered_df.empty:
    st.dataframe(filtered_df[show_cols])
else:
    st.info("No data matches the selected filters. Try adjusting them.")
