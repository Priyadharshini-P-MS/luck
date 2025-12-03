import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------- Page config -----------------
st.set_page_config(
    page_title="Witness Archive: ICE Raids in Chicago",
    page_icon="📚",
    layout="wide",
)


# ----------------- Helpers -----------------
def pick_column(df, candidates, default=None):
    """Return the first column name from candidates that exists in df."""
    for c in candidates:
        if c in df.columns:
            return c
    return default


@st.cache_data
def load_data():
    df = pd.read_csv("ICE_Chicago_REAL_dataset.csv")

    # Try to detect key columns
    title_col = pick_column(df, ["Title", "Article Title", "Headline"])
    emotion_col = pick_column(df, ["Emotion", "Primary Emotion", "emotion_label"])
    theme_col = pick_column(df, ["Theme", "Primary Theme", "Topic"])
    source_col = pick_column(df, ["Source", "Outlet", "Publication"])
    date_col = pick_column(df, ["Publication Date", "Date", "Published", "Date Published"])
    text_col = pick_column(
        df,
        ["Quote", "Narrative", "Excerpt", "Snippet", "Summary", "Full Text", "Text", "Content", "Body"],
    )
    url_col = pick_column(df, ["URL", "Link", "Article URL"])

    # Convert dates, if present
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    meta = {
        "title_col": title_col,
        "emotion_col": emotion_col,
        "theme_col": theme_col,
        "source_col": source_col,
        "date_col": date_col,
        "text_col": text_col,
        "url_col": url_col,
    }
    return df, meta


df, meta = load_data()

title_col = meta["title_col"]
emotion_col = meta["emotion_col"]
theme_col = meta["theme_col"]
source_col = meta["source_col"]
date_col = meta["date_col"]
text_col = meta["text_col"]
url_col = meta["url_col"]

# ----------------- Header -----------------
st.markdown(
    "<h1 style='margin-bottom:0'>Witness Archive: Chicago ICE Enforcement</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#666; margin-top:0.3rem; margin-bottom:1rem'>"
    "Interactive dashboard for exploring testimonies, emotions, themes, and news sources "
    "from the Chicago ICE raids corpus."
    "</p>",
    unsafe_allow_html=True,
)

with st.expander("Detected columns (for debugging)", expanded=False):
    st.write(meta)

# ----------------- Sidebar Filters -----------------
st.sidebar.title("Filters")

# Emotion filter
if emotion_col:
    emotion_values = sorted(df[emotion_col].dropna().unique())
    selected_emotions = st.sidebar.multiselect(
        "Emotion", options=emotion_values, default=emotion_values
    )
else:
    selected_emotions = None

# Theme filter
if theme_col:
    theme_values = sorted(df[theme_col].dropna().unique())
    selected_themes = st.sidebar.multiselect(
        "Theme", options=theme_values, default=theme_values
    )
else:
    selected_themes = None

# Source filter (handles hundreds of sources)
if source_col:
    all_sources = sorted(df[source_col].dropna().unique().tolist())
    st.sidebar.caption(f"Total unique sources: {len(all_sources)}")

    source_search = st.sidebar.text_input(
        "Filter sources by name (optional)", value="", placeholder="Type part of name…"
    )

    if source_search:
        filtered_sources_list = [s for s in all_sources if source_search.lower() in str(s).lower()]
    else:
        filtered_sources_list = all_sources

    selected_sources = st.sidebar.multiselect(
        "Sources (scroll for more)",
        options=filtered_sources_list,
        default=filtered_sources_list,  # select all visible by default
    )
else:
    selected_sources = None

# Date range filter
if date_col:
    min_date = df[date_col].min()
    max_date = df[date_col].max()
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

# ----------------- Apply Filters -----------------
filtered_df = df.copy()

if emotion_col and selected_emotions:
    filtered_df = filtered_df[filtered_df[emotion_col].isin(selected_emotions)]

if theme_col and selected_themes:
    filtered_df = filtered_df[filtered_df[theme_col].isin(selected_themes)]

if source_col and selected_sources:
    filtered_df = filtered_df[filtered_df[source_col].isin(selected_sources)]

if date_col and start_date and end_date:
    mask = (
        filtered_df[date_col].dt.date >= start_date
    ) & (
        filtered_df[date_col].dt.date <= end_date
    )
    filtered_df = filtered_df[mask]

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

col_a, col_b, col_c, col_d = st.columns(4)

with col_a:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Total rows", len(df))
    st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("After filters", len(filtered_df))
    st.markdown("</div>", unsafe_allow_html=True)

with col_c:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    if source_col:
        st.metric("Unique sources", df[source_col].nunique())
    else:
        st.metric("Unique sources", "—")
    st.markdown("</div>", unsafe_allow_html=True)

with col_d:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    if date_col and df[date_col].notna().any():
        date_min = df[date_col].min().date()
        date_max = df[date_col].max().date()
        st.metric("Date range", f"{date_min} → {date_max}")
    else:
        st.metric("Date range", "—")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ----------------- Tabs Layout -----------------
tab_overview, tab_emotions, tab_sources, tab_data = st.tabs(
    ["📈 Time & counts", "🎭 Emotions & themes", "📰 Sources", "📑 Data & testimony viewer"]
)

# ----- Tab 1: Time & counts -----
with tab_overview:
    if date_col and not filtered_df.empty:
        by_date = (
            filtered_df.dropna(subset=[date_col])
            .groupby(filtered_df[date_col].dt.date)
            .size()
            .reset_index(name="Count")
            .sort_values(date_col)
        )
        fig_time = px.line(
            by_date,
            x=date_col,
            y="Count",
            markers=True,
            title="Number of testimonies over time",
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No valid date column available for timeline chart.")


# ----- Tab 2: Emotions & themes -----
with tab_emotions:
    c1, c2 = st.columns(2)

    if emotion_col and not filtered_df.empty:
        emotion_counts = (
            filtered_df[emotion_col]
            .value_counts()
            .reset_index()
            .rename(columns={emotion_col: "Count", "index": "Emotion"})
        )

        with c1:
            fig_bar_emotion = px.bar(
                emotion_counts,
                x="Emotion",
                y="Count",
                title="Emotion distribution (bar)",
            )
            st.plotly_chart(fig_bar_emotion, use_container_width=True)

        with c2:
            fig_pie_emotion = px.pie(
                emotion_counts,
                names="Emotion",
                values="Count",
                title="Emotion share (pie)",
                hole=0.3,
            )
            st.plotly_chart(fig_pie_emotion, use_container_width=True)
    else:
        st.info("No emotion column found or no data after filters.")

    st.markdown("---")

    if theme_col and not filtered_df.empty:
        theme_counts = (
            filtered_df[theme_col]
            .value_counts()
            .reset_index()
            .rename(columns={theme_col: "Count", "index": "Theme"})
        )
        fig_theme = px.bar(
            theme_counts,
            x="Theme",
            y="Count",
            title="Theme distribution",
        )
        st.plotly_chart(fig_theme, use_container_width=True)
    else:
        st.info("No theme column found or no data after filters.")


# ----- Tab 3: Sources -----
with tab_sources:
    if source_col and not filtered_df.empty:
        src_counts = (
            filtered_df[source_col]
            .value_counts()
            .reset_index()
            .rename(columns={source_col: "Count", "index": "Source"})
        )

        st.caption(f"Total unique sources in filtered data: {src_counts['Source'].nunique()}")

        fig_src_top = px.bar(
            src_counts.head(25),
            x="Source",
            y="Count",
            title="Top sources by number of testimonies (top 25)",
        )
        fig_src_top.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_src_top, use_container_width=True)

        if emotion_col:
            by_src_emotion = (
                filtered_df.groupby([source_col, emotion_col])
                .size()
                .reset_index(name="Count")
            )
            fig_src_emotion = px.bar(
                by_src_emotion,
                x=source_col,
                y="Count",
                color=emotion_col,
                title="Emotion by source (stacked)",
            )
            fig_src_emotion.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_src_emotion, use_container_width=True)
    else:
        st.info("No source column found or no data after filters.")


# ----- Tab 4: Data & testimony viewer -----
with tab_data:
    if filtered_df.empty:
        st.info("No rows match the current filters. Try relaxing them.")
    else:
        # sort by date if possible
        if date_col:
            filtered_df = filtered_df.sort_values(date_col, ascending=False)

        # Build labels for dropdown
        labels = []
        indices = []

        for idx, row in filtered_df.iterrows():
            title_val = str(row[title_col]) if title_col and pd.notna(row[title_col]) else "Untitled"
            source_val = str(row[source_col]) if source_col and pd.notna(row[source_col]) else "Unknown source"
            if date_col and pd.notna(row[date_col]):
                date_val = row[date_col].strftime("%Y-%m-%d")
            else:
                date_val = "No date"

            label = f"{title_val} — {source_val} — {date_val}"
            labels.append(label)
            indices.append(idx)

        selected_label = st.selectbox("Choose a testimony", options=labels)
        selected_index = indices[labels.index(selected_label)]
        selected_row = filtered_df.loc[selected_index]

        left, right = st.columns([2, 3])

        # ---- Left: quote/details card ----
        with left:
            st.markdown("<div class='quote-card'>", unsafe_allow_html=True)

            title_val = (
                str(selected_row[title_col])
                if title_col and pd.notna(selected_row[title_col])
                else "Untitled testimony"
            )
            st.markdown(f"### {title_val}")

            meta_parts = []
            if source_col and pd.notna(selected_row.get(source_col, None)):
                meta_parts.append(str(selected_row[source_col]))
            if date_col and pd.notna(selected_row.get(date_col, None)):
                meta_parts.append(selected_row[date_col].strftime("%Y-%m-%d"))
            if emotion_col and pd.notna(selected_row.get(emotion_col, None)):
                meta_parts.append(f"Emotion: {selected_row[emotion_col]}")
            if theme_col and pd.notna(selected_row.get(theme_col, None)):
                meta_parts.append(f"Theme: {selected_row[theme_col]}")

            if meta_parts:
                meta_html = " • ".join(meta_parts)
                st.markdown(f"<div class='meta-line'>{meta_html}</div>", unsafe_allow_html=True)

            # Show main narrative text
            if text_col and pd.notna(selected_row.get(text_col, None)):
                st.write(selected_row[text_col])
            else:
                st.write("No narrative text available for this entry.")

            # URL link
            if url_col and pd.notna(selected_row.get(url_col, None)):
                url_val = str(selected_row[url_col])
                st.markdown(f"[Open original article]({url_val})")

            st.markdown("</div>", unsafe_allow_html=True)

        # ---- Right: table ----
        with right:
            st.caption("Filtered dataset (first 200 rows). Scroll horizontally for more columns.")
            display_cols = []
            for c in [title_col, emotion_col, theme_col, source_col, date_col, url_col]:
                if c and c not in display_cols:
                    display_cols.append(c)
            # add some extra cols if needed
            for c in df.columns:
                if c not in display_cols:
                    display_cols.append(c)

            st.dataframe(filtered_df[display_cols].head(200), use_container_width=True)
