import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------- Page config -----------------
st.set_page_config(
    page_title="Witness Archive: ICE Raids in Chicago",
    page_icon="📚",
    layout="wide",
)

# ----------------- Load data -----------------
@st.cache_data
def load_data():
    df = pd.read_csv("ICE_Chicago_REAL_dataset.csv")

    # Make sure publication date is datetime if present
    if "Publication Date" in df.columns:
        df["Publication Date"] = pd.to_datetime(df["Publication Date"], errors="coerce")

    return df

df = load_data()

# ----------------- Helper to pick text column -----------------
TEXT_COLUMN_CANDIDATES = [
    "Quote",
    "Excerpt",
    "Snippet",
    "Summary",
    "Full Text",
    "Text",
    "Narrative",
    "Content",
]

def get_text_column(dataframe):
    for col in TEXT_COLUMN_CANDIDATES:
        if col in dataframe.columns:
            return col
    return None

text_col = get_text_column(df)

# ----------------- Title / subtitle -----------------
st.markdown(
    "<h1 style='margin-bottom:0'>Witness Archive: Chicago ICE Enforcement</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#666; margin-top:0.3rem; margin-bottom:1rem'>"
    "Interactive dashboard to explore testimonies, emotions, themes, and timeline "
    "from the ICE raids corpus."
    "</p>",
    unsafe_allow_html=True,
)

# ----------------- Sidebar filters (NO source filter) -----------------
st.sidebar.title("Filters")

# Emotion filter
if "Emotion" in df.columns:
    all_emotions = sorted(df["Emotion"].dropna().unique())
    selected_emotions = st.sidebar.multiselect(
        "Emotion", options=all_emotions, default=all_emotions
    )
else:
    selected_emotions = None

# Theme filter
if "Theme" in df.columns:
    all_themes = sorted(df["Theme"].dropna().unique())
    selected_themes = st.sidebar.multiselect(
        "Theme", options=all_themes, default=all_themes
    )
else:
    selected_themes = None

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

# ----------------- Apply filters -----------------
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
    date_mask = (
        filtered_df["Publication Date"].dt.date >= start_date
    ) & (
        filtered_df["Publication Date"].dt.date <= end_date
    )
    filtered_df = filtered_df[date_mask]

# ----------------- Light CSS styling -----------------
st.markdown(
    """
    <style>
    .metric-card {
        padding: 1rem 1.25rem;
        border-radius: 0.9rem;
        border: 1px solid #eeeeee;
        background-color: #fafafa;
    }
    .quote-card {
        padding: 1.5rem;
        border-radius: 0.9rem;
        border: 1px solid #eeeeee;
        background-color: #ffffff;
    }
    .meta-line {
        color: #777;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------- Overview metrics -----------------
st.subheader("Overview")

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Total testimonies", len(df))
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("After filters", len(filtered_df))
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ----------------- Tabs -----------------
tab_emotions, tab_timeline, tab_viewer = st.tabs(
    ["🎭 Emotions & themes", "📈 Timeline", "📑 Testimony viewer"]
)

# ----- Tab 1: Emotions & themes -----
with tab_emotions:
    if filtered_df.empty:
        st.info("No data after filters. Try relaxing them.")
    else:
        col_e1, col_e2 = st.columns(2)

        # Emotion charts
        if "Emotion" in filtered_df.columns:
            emotion_counts = (
                filtered_df["Emotion"]
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Emotion", "Emotion": "Count"})
            )

            with col_e1:
                fig_em_bar = px.bar(
                    emotion_counts,
                    x="Emotion",
                    y="Count",
                    title="Emotion distribution (bar)",
                )
                st.plotly_chart(fig_em_bar, use_container_width=True)

            with col_e2:
                fig_em_pie = px.pie(
                    emotion_counts,
                    names="Emotion",
                    values="Count",
                    title="Emotion share (pie)",
                    hole=0.3,
                )
                st.plotly_chart(fig_em_pie, use_container_width=True)
        e
