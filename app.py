import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Witness Archive: ICE Raid Testimonies",
    page_icon="📚",
    layout="wide",
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("ICE_Chicago_verified_dataset.csv")

    # Convert date
    if "Publication Date" in df.columns:
        df["Publication Date"] = pd.to_datetime(df["Publication Date"], errors="coerce")

    return df

df = load_data()

# Column mapping
TITLE_COL = "Title"
URL_COL = "URL"
SOURCE_COL = "Source"
DATE_COL = "Publication Date"
TEXT_COL = "Summary"
EMOTION_COL = "Emotion Label"
THEME_COL = "Thematic Label"

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("<h1 style='margin:0;'>Witness Archive Dashboard</h1>", unsafe_allow_html=True)
st.write("Explore emotions, themes, sources, and testimonies related to ICE enforcement.")

st.markdown("---")

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("Filters")

# Emotion filter
emotions = sorted(df[EMOTION_COL].dropna().unique())
selected_emotions = st.sidebar.multiselect(
    "Emotion", options=emotions, default=emotions
)

# Theme filter
themes = sorted(df[THEME_COL].dropna().unique())
selected_themes = st.sidebar.multiselect(
    "Theme", options=themes, default=themes
)

# Date range filter
if df[DATE_COL].notna().any():
    min_date = df[DATE_COL].min().date()
    max_date = df[DATE_COL].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Publication Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
else:
    start_date, end_date = None, None

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
filtered = df.copy()

filtered = filtered[filtered[EMOTION_COL].isin(selected_emotions)]
filtered = filtered[filtered[THEME_COL].isin(selected_themes)]

if start_date and end_date:
    mask = (filtered[DATE_COL].dt.date >= start_date) & (filtered[DATE_COL].dt.date <= end_date)
    filtered = filtered[mask]

# --------------------------------------------------
# METRICS
# --------------------------------------------------
c1, c2, c3 = st.columns(3)

c1.metric("Total Records", len(df))
c2.metric("Filtered Records", len(filtered))
c3.metric("Unique Sources", df[SOURCE_COL].nunique())

st.markdown("---")

# --------------------------------------------------
# EMOTION & THEME CHARTS
# --------------------------------------------------
ec1, ec2 = st.columns(2)

with ec1:
    emotion_counts = filtered[EMOTION_COL].value_counts().reset_index()
    emotion_counts.columns = [EMOTION_COL, "Count"]
    fig_em_bar = px.bar(emotion_counts, x=EMOTION_COL, y="Count",
                        title="Emotion Distribution (Bar)")
    st.plotly_chart(fig_em_bar, use_container_width=True)

with ec2:
    fig_em_pie = px.pie(emotion_counts, names=EMOTION_COL, values="Count",
                        title="Emotion Distribution (Pie)", hole=0.3)
    st.plotly_chart(fig_em_pie, use_container_width=True)

# Theme Chart
theme_counts = filtered[THEME_COL].value_counts().reset_index()
theme_counts.columns = [THEME_COL, "Count"]
fig_theme = px.bar(theme_counts, x=THEME_COL, y="Count", title="Theme Distribution")
st.plotly_chart(fig_theme, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# TIMELINE CHART
# --------------------------------------------------
if filtered[DATE_COL].notna().any():
    date_counts = (
        filtered.dropna(subset=[DATE_COL])
        .groupby(filtered[DATE_COL].dt.date)
        .size()
        .reset_index(name="Count")
    )
    fig_time = px.line(
        date_counts,
        x="Publication Date",
        y="Count",
        title="Publications Over Time",
        markers=True,
    )
    st.plotly_chart(fig_time, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# TESTIMONY VIEWER
# --------------------------------------------------
st.subheader("Testimony Viewer")

if filtered.empty:
    st.info("No testimonies match the current filters.")
else:
    # Sort by date
    filtered = filtered.sort_values(DATE_COL, ascending=False)

    # Build labels
    labels = []
    for _, row in filtered.iterrows():
        title = row[TITLE_COL] if pd.notna(row[TITLE_COL]) else "Untitled"
        date_text = row[DATE_COL].strftime("%Y-%m-%d") if pd.notna(row[DATE_COL]) else "No date"
        labels.append(f"{title} — {date_text}")

    selected = st.selectbox("Select a testimony", labels)
    idx = labels.index(selected)
    row = filtered.iloc[idx]

    st.write(f"### {row[TITLE_COL]}")

    meta_parts = [
        f"Emotion: {row[EMOTION_COL]}",
        f"Theme: {row[THEME_COL]}",
        f"Source: {row[SOURCE_COL]}",
    ]
    if pd.notna(row[DATE_COL]):
        meta_parts.append(row[DATE_COL].strftime("%Y-%m-%d"))

    st.write(", ".join(meta_parts))

    st.write("---")

    # Narrative Text
    st.write(row[TEXT_COL])

    # URL
    if pd.notna(row[URL_COL]):
        st.markdown(f"[Open original article]({row[URL_COL]})")

st.markdown("---")

# --------------------------------------------------
# DATA TABLE
# --------------------------------------------------
st.subheader("Filtered Data Table")
st.dataframe(filtered.head(200))
