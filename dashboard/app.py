import streamlit as st
import pandas as pd
import sqlite3
from urllib.parse import urlparse
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------------------------
# Load Data from SQLite
# ---------------------------
conn = sqlite3.connect("db/articles.db")
df = pd.read_sql_query("SELECT * FROM articles", conn)
conn.close()

st.title("🛰️ Defense & Security Intelligence Dashboard")

st.markdown("""
This dashboard provides insights from open-source defense & security articles.""")

# ---------------------------
# Interactive Table with Text Toggle
# ---------------------------
# ---------------------------
# 📄 EXPLORE ARTICLES
# ---------------------------
st.header("📄 Explore Articles")

# Text mode toggle
view_mode = st.radio("Text Display Mode:", ["Translated", "Original"], horizontal=True)

if view_mode == "Translated":
    df["text_display"] = df["content_translated"]
else:
    df["text_display"] = df["content_raw"]

# Filters row
col1, col2 = st.columns(2)
with col1:
    publisher_list = ["All"] + sorted(df["publisher"].dropna().unique().tolist())
    publisher_filter = st.selectbox("Filter by Publisher:", publisher_list)
with col2:
    language_list = ["All"] + sorted(df["language"].dropna().unique().tolist())
    language_filter = st.selectbox("Filter by Language:", language_list)

# Apply filters
filtered = df.copy()
if publisher_filter != "All":
    filtered = filtered[filtered["publisher"] == publisher_filter]
if language_filter != "All":
    filtered = filtered[filtered["language"] == language_filter]

# Display table
st.dataframe(filtered[["pub_date", "publisher", "language", "title", "text_display", "url"]])

# Download button
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

csv_data = convert_df_to_csv(filtered[["pub_date", "publisher", "language", "title", "text_display", "url"]])

st.download_button(
    label="⬇️ Download Filtered Results as CSV",
    data=csv_data,
    file_name="filtered_articles.csv",
    mime="text/csv"
)

# ---------------------------
# Global Metrics
# ---------------------------
col1, col2 = st.columns(2)
col1.metric("Total Articles", len(df))
col2.metric("Unique Publishers", df["publisher"].nunique())

# ---------------------------
# Article Volume Over Time
# ---------------------------
st.header("📅 Articles Over Time")
df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce")
articles_per_day = df.groupby(df["pub_date"].dt.date).size()
st.line_chart(articles_per_day)

# ---------------------------
# ☁️ Global Tag Cloud (Exam Requirement)
# ---------------------------
st.header("☁️ Global Tag Cloud (All Articles)")

text = " ".join(df["content_clean"])

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    wordcloud = WordCloud(
        width=1200,
        height=400,
        background_color="white",
        max_words=200
    ).generate(text)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

except Exception as e:
    st.error("WordCloud failed to generate. Error: {}".format(e))

# ---------------------------
# Top Publishers
# ---------------------------
st.header("🌍 Top Sources (Publishers)")
top_publishers = df["publisher"].value_counts().head(10)
st.bar_chart(top_publishers)

# ---------------------------
# 🎯 Keyword Frequency Per Publisher
# ---------------------------
st.header("🎯 Keyword Frequency by Publisher")

# Publisher selector
publisher_kw = st.selectbox("Select Publisher for Keyword Analysis:", sorted(df["publisher"].unique()))

# Filter dataset
pub_df = df[df["publisher"] == publisher_kw]

# Extract keywords from cleaned text
from collections import Counter
all_words = " ".join(pub_df["content_clean"]).split()
word_counts = Counter(all_words).most_common(10)

# Convert to DataFrame for plotting
kw_df = pd.DataFrame(word_counts, columns=["keyword", "count"])

st.bar_chart(kw_df.set_index("keyword"))
# ---------------------------
# 📈 Publisher Activity Over Time
# ---------------------------
st.header("📈 Publisher Activity Over Time")

# Ensure pub_date is datetime
df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce")

# Same UI style as Explore Articles (one line)
col1 = st.columns(1)[0]

publisher_list = sorted(df["publisher"].unique())
selected_publisher = col1.selectbox("Select Publisher:", publisher_list)

# Filter to selected publisher
trend_df = df[df["publisher"] == selected_publisher] \
    .groupby(df["pub_date"].dt.date) \
    .size() \
    .reset_index(name="count")

# Line chart
st.line_chart(trend_df.set_index("pub_date"))

# ---------------------------
# 🌍 Country Mention Frequency
# ---------------------------
st.header("🌍 Country Mentions in Articles")

# Simple country name list (can be expanded easily later)
countries = [
    "united states", "usa", "america",
    "russia", "china", "ukraine", "belarus",
    "poland", "france", "germany", "uk", "britain",
    "israel", "iran", "turkey", "india", "pakistan",
    "north korea", "south korea", "japan",
    "australia", "canada", "brazil"
]

# Count frequency in content_clean
from collections import Counter
word_list = " ".join(df["content_clean"]).split()
counter = Counter(word_list)

country_counts = []
for c in countries:
    c_words = c.split()
    if len(c_words) == 1:
        count = counter.get(c_words[0], 0)
    else:
        # handle multi-word countries e.g., "united states"
        count = df["content_clean"].str.contains(c.replace(" ", " "), case=False).sum()
    country_counts.append((c, count))

country_df = pd.DataFrame(country_counts, columns=["country", "count"])
country_df = country_df.sort_values("count", ascending=False).head(12)

st.bar_chart(country_df.set_index("country"))

