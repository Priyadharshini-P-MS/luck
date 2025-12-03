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

def get_url_column(dataframe):
    # Try common URL column names
    for col in ["URL", "Url", "url", "Link", "Article URL"]:
        if col in dataframe.columns:
            return col
    return None

url_col = get_url_column(df)

# Create simple URL validity flag (Original vs Missing/Dummy)
if url_col:
    df["URL Status"] = df[url_col].apply(
        lambda x: "Original URL" if isinstance(x, str) and x.startswith("http") else "Missing / Dummy"
    )

# ---------- Title ----------
st.title("Witness Archive: Chicago ICE Enforcement")
st.write(
    "Simple interactive dashboard to explore testimonies, emotions, themes, URLs, "
    "and the timeline from the ICE raids corpus."
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

# Optional: filter by URL status
if url_col:
    url_status_options = ["All", "Original URL only", "Missing / Dummy only"]
    selected_url_status = st.sidebar.selectbox(
        "URL filter", options=url_status_options, index=0
    )
else:
    selected_url_status = "All"

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

if url_col and "URL Status" in filtered_df.columns:
    if selected_url_status == "Original URL only":
        filtered_df = filtered_df[filtered_df["URL Status"] == "Original URL"]
    elif selected_url_status == "Missing / Dummy only":
        filtered_df = filtered_df[filtered_df["URL Status"] == "Missing / Dummy"]

# ---------- Overview ----------
st.subheader("Overview")
c1, c2, c3 = st.columns(3)
c1.metric("Total rows", len(df))
c2.metric("Filtered rows", len(filtered_df))
if url_col and "URL Status" in df.columns:
    c3.metric(
        "Rows with original URL",
        int((df["URL Status"] == "Original URL").sum()),
    )
else:
    c3.metric("Rows with original URL", "N/A")

st.markdown("---")

# ---------- Charts ----------
# Emotion bar + pie charts
if not filtered_df.empty and "Emotion" in filtered_df.columns:
    emotion_counts = filtered_df["Emotion"].value_counts().reset_index()
    emotion_counts.columns = ["Emotion", "Count"]

    col_em1, col_em2 = st.columns(2)

    with col_em1:
        fig_emotion_bar = px.bar(
            emotion_counts,
            x="Emotion",
            y="Count",
            title="Emotion distribution (bar)",
        )
        st.plotly_chart(fig_emotion_bar, use_container_width=True)

    with col_em2:
        fig_emotion_pie = px.pie(
            emotion_counts,
            names="Emotion",
            values="Count",
            title="Emotion distribution (pie)",
            hole=0.3,
        )
        st.plotly_chart(fig_emotion_pie, use_container_width=True)

# Theme bar chart
if not filtered_df.empty and "Theme" in filtered_df.columns:
    theme_counts = filtered_df["Theme"].value_counts().reset_index()
    theme_counts.columns = ["Theme", "Count"]
    fig_theme = px.bar(
        theme_counts,
        x="Theme",
        y="Count",
        title="Theme distribution (bar)",
    )
    st.plotly_chart(fig_theme, use_container_width=True)

# Timeline chart
if (
    not filtered_df.empty
    and "Publication Date" in filtered_df.columns
    and filtered_df["Publication Date"].notna().any()
):
    by_date = (
        filtered_df.dropna(subset=["Publication Date"])
        .groupby(filtered_df["Publication Date"].dt.date)
        .size()
        .reset_index(name="Count")
        .sort_values("Publication Date")
    )
    if not by_date.empty:
        fig_time = px.line(
            by_date,
            x="Publication Date",
            y="Count",
            markers=True,
            title="Number of testimonies over time",
        )
        st.plotly_chart(fig_time, use_container_width=True)

st.markdown("---")

# ---------- Testimony viewer ----------
st.subheader("Testimony viewer")

if filtered_df.empty:
    st.info("No rows match current filters. Try relaxing them.")
else:
    # Sort newest first if possible
    if "Publication Date" in filtered_df.columns:
        filtered_df = filtered_df.sort_values("Publication Date", ascending=False)

    # Build dropdown labels
    options = []
    for _, row in filtered_df.iterrows():
        if "Title" in filtered_df.columns and pd.notna(row.get("Title")):
            title = str(row["Title"])
        else:
            title = "Untitled"
        label = title
        if "Publication Date" in filtered_df.columns and pd.notna(row.get("Publication Date")):
            date_str = row["Publication Date"].strftime("%Y-%m-%d")
            label = f"{title} ({date_str})"
        options.append(label)

    selected_label = st.selectbox("Choose a testimony", options=options)
    selected_index = options.index(selected_label)
    selected_row = filtered_df.iloc[selected_index]

    # Title
    if "Title" in selected_row.index:
        st.write("###", selected_row["Title"])

    # Meta info
    meta_parts = []
    if "Emotion" in selected_row.index and pd.notna(selected_row.get("Emotion")):
        meta_parts.append(f"Emotion: {selected_row['Emotion']}")
    if "Theme" in selected_row.index and pd.notna(selected_row.get("Theme")):
        meta_parts.append(f"Theme: {selected_row['Theme']}")
    if "Publication Date" in selected_row.index and pd.notna(selected_row.get("Publication Date")):
        meta_parts.append(selected_row["Publication Date"].strftime("%Y-%m-%d"))
    if url_col and url_col in selected_row.index and pd.notna(selected_row.get(url_col)):
        meta_parts.append("Has URL")
    else:
        meta_parts.append("No URL / dummy")
    if meta_parts:
        st.write(", ".join(meta_parts))

    # Narrative text
    text_columns = [
        "Quote",
        "Excerpt",
        "Snippet",
        "Summary",
        "Full Text",
        "Text",
        "Narrative",
        "Content",
    ]
    text_value = None
    for col in text_columns:
        if col in selected_row.index and pd.notna(selected_row.get(col)):
            text_value = selected_row[col]
            break

    if text_value is not None:
        st.write(text_value)
    else:
        st.write("No narrative text available for this row.")

    # URL (clickable) if present
    if url_col and url_col in selected_row.index and pd.notna(selected_row.get(url_col)):
        st.markdown(f"[Open original article]({selected_row[url_col]})")

st.markdown("---")

# ---------- Show filtered data, including URL status ----------
st.subheader("Filtered data (first 200 rows)")
display_cols = list(filtered_df.columns)
if "URL Status" in display_cols and url_col and url_col in display_cols:
    # Move URL Status next to URL column
    display_cols.remove("URL Status")
    url_index = display_cols.index(url_col)
    display_cols.insert(url_index + 1, "URL Status")

st.dataframe(filtered_df[display_cols].head(200))
