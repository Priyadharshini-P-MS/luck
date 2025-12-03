import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Page settings ----------
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

# ---------- Title + subtitle ----------
st.markdown(
    "<h1 style='margin-bottom:0'>Witness Archive: Chicago ICE Enforcement</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#666; margin-top:0.25rem; margin-bottom:1rem'>"
    "Explore testimonies, emotions, themes, and sources from the ICE raids corpus."
    "</p>",
    unsafe_allow_html=True,
)

# ---------- Sidebar filters ----------
st.sidebar.title("Filters")

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

# ---------- Light styling ----------
st.markdown(
    '''
    <style>
    .metric-card {
        padding: 1rem 1.25rem;
        border-radius: 0.75rem;
        border: 1px solid #eee;
        background-color: #fafafa;
    }
    .quote-card {
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #eee;
        background-color: #ffffff;
    }
    .meta-line {
        color: #777;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }
    </style>
    ''',
    unsafe_allow_html=True,
)

# ---------- Overview metrics ----------
st.subheader("Overview")

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Total testimonies", len(df))
    st.markdown("</div>", unsafe_allow_html=True)

with m2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("After filters", len(filtered_df))
    st.markdown("</div>", unsafe_allow_html=True)

with m3:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    if "Source" in df.columns:
        st.metric("Unique sources", df["Source"].nunique())
    else:
        st.metric("Unique sources", "N/A")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------- Charts row ----------
left_charts, right_charts = st.columns(2)

with left_charts:
    if "Emotion" in filtered_df.columns and not filtered_df.empty:
        emotion_counts = (
            filtered_df["Emotion"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Emotion", "Emotion": "Count"})
        )
        fig_emotion = px.bar(
            emotion_counts,
            x="Emotion",
            y="Count",
            title="Emotion distribution",
        )
        st.plotly_chart(fig_emotion, use_container_width=True)

with right_charts:
    if "Theme" in filtered_df.columns and not filtered_df.empty:
        theme_counts = (
            filtered_df["Theme"]
            .value_counts()
            .reset_index()
            .rename(columns={"index": "Theme", "Theme": "Count"})
        )
        fig_theme = px.bar(
            theme_counts,
            x="Theme",
            y="Count",
            title="Theme distribution",
        )
        st.plotly_chart(fig_theme, use_container_width=True)

st.markdown("---")

# ---------- Testimony explorer ----------
st.subheader("Testimony explorer")

if filtered_df.empty:
    st.info("No data matches the selected filters. Try relaxing them to see testimonies.")
else:
    # newest first if date exists
    if "Publication Date" in filtered_df.columns:
        filtered_df = filtered_df.sort_values("Publication Date", ascending=False)

    # Build nice labels for dropdown
    label_to_index = {}
    labels = []

    for idx, row in filtered_df.iterrows():
        title = row["Title"] if "Title" in row and pd.notna(row["Title"]) else "Untitled"
        pieces = []
        if "Source" in row and pd.notna(row["Source"]):
            pieces.append(str(row["Source"]))
        if "Publication Date" in row and pd.notna(row["Publication Date"]):
            pieces.append(row["Publication Date"].strftime("%Y-%m-%d"))

        label = title
        if pieces:
            label = f"{title} — " + " | ".join(pieces)

        label_to_index[label] = idx
        labels.append(label)

    selected_label = st.selectbox("Choose a testimony", options=labels)
    selected_row = filtered_df.loc[label_to_index[selected_label]]

    viewer_col, table_col = st.columns([2, 3])

    # ---- Left: quote card ----
    with viewer_col:
        st.markdown("<div class='quote-card'>", unsafe_allow_html=True)

        title_text = (
            selected_row["Title"]
            if "Title" in selected_row and pd.notna(selected_row["Title"])
            else "Untitled"
        )
        st.markdown(f"### {title_text}")

        meta_parts = []
        if "Source" in selected_row and pd.notna(selected_row["Source"]):
            meta_parts.append(str(selected_row["Source"]))
        if "Publication Date" in selected_row and pd.notna(selected_row["Publication Date"]):
            meta_parts.append(selected_row["Publication Date"].strftime("%Y-%m-%d"))
        if "Emotion" in selected_row and pd.notna(selected_row["Emotion"]):
            meta_parts.append(f"Emotion: {selected_row['Emotion']}")
        if "Theme" in selected_row and pd.notna(selected_row["Theme"]):
            meta_parts.append(f"Theme: {selected_row['Theme']}")

        if meta_parts:
            meta_html = " • ".join(meta_parts)
            st.markdown(f"<div class='meta-line'>{meta_html}</div>", unsafe_allow_html=True)

        text_column_candidates = [
            "Quote",
            "Excerpt",
            "Snippet",
            "Summary",
            "Full Text",
            "Text",
        ]
        text_to_show = None
        for c in text_column_candidates:
            if c in selected_row and pd.notna(selected_row[c]):
                text_to_show = selected_row[c]
                break

        if text_to_show:
            st.write(text_to_show)
        else:
            st.write("No narrative text available for this entry.")

        if "URL" in selected_row and pd.notna(selected_row["URL"]):
            st.markdown(f"[Open original article]({selected_row['URL']})")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Right: filtered table ----
    with table_col:
        st.caption("Filtered dataset (top 200 rows)")
        show_cols = [
            c
            for c in ["Title", "Emotion", "Theme", "Source", "Publication Date", "URL"]
            if c in filtered_df.columns
        ]
        st.dataframe(filtered_df[show_cols].head(200), use_container_width=True)
