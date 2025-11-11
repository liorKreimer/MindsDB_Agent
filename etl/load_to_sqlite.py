import pandas as pd
import sqlite3
import re
import nltk
from nltk.corpus import stopwords
from pathlib import Path
from urllib.parse import urlparse
from langdetect import detect, LangDetectException
from transformers import MarianMTModel, MarianTokenizer
import torch
from tqdm import tqdm


# Download stopwords (only runs first time)
nltk.download("stopwords", quiet=True)
stop_words = set(stopwords.words("english"))
CUSTOM_STOPWORDS = {
    "said", "say", "says", "one", "two", "also", "would", "could",
    "zzz", "zz", "zzzz", "tag", "tags"
}  # Custom stopwords to remove problematic noise terms (see in tag cloud from articles content )


# Load translation model one time
model_name = "Helsinki-NLP/opus-mt-mul-en"   # Multi-language → English
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)
# -----------------------------
# 1) Make sure the database folder exists
# -----------------------------
Path("db").mkdir(exist_ok=True)

# -----------------------------
# 2) Load the original CSV into memory
# -----------------------------
df = pd.read_csv("data/datanalystexam.csv", on_bad_lines="skip")
df.columns = [str(c) for c in df.columns]  # ensure consistent column names

# -----------------------------
# 3) Identify the columns we care about (by position) In the original DataSet
# -----------------------------
date_col = df.columns[4]        # publication date column
url_col = df.columns[7]         # article source URL column (not image URL)
content_col = df.columns[9]     # article text / summary column
title_col = df.columns[11]      # article title column

# -----------------------------
# 4) Create a new simplified dataframe with the selected fields
# -----------------------------
clean = pd.DataFrame()
clean["pub_date"] = pd.to_datetime(df[date_col], errors="coerce")  # convert to date
clean["url"] = df[url_col].astype(str).str.strip()                 # store URL as text
clean["publisher"] = clean["url"].apply(
    lambda x: urlparse(x).netloc.replace("www.", "") if isinstance(x, str) else None
)  # Extract publisher domain from the URL
clean["title"] = df[title_col].astype(str).str.strip()             # original article title
clean["content_raw"] = df[content_col].astype(str).str.strip()     # original article text
# -----------------------------
# 5) Define the detect language --> translate_to_english -->  Light Clean text
# -----------------------------
# Language detection function
def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"
clean["language"] = clean["content_raw"].apply(detect_language)  # Detect language of the content

# Translate non-English content
tqdm.pandas()  # progress bar for translate steps
def translate_if_needed(text, lang):
    if lang == "en":
        return text  # English stays as-is
    try:
        batch = tokenizer([text], return_tensors="pt", padding=True, truncation=True)
        translated = model.generate(**batch)
        return tokenizer.decode(translated[0], skip_special_tokens=True)
    except:
        return text  # fallback: keep original

clean["content_translated"] = clean.progress_apply(
    lambda row: translate_if_needed(row["content_raw"], row["language"]),
    axis=1
) # Translate content to English IF needed

# clean text function after all the content is in English
def clean_text(text):
    text = text.lower()                                          # convert to lowercase
    tokens = re.findall(r"[a-z]+", text)                  # extract only alphabetic tokens
    tokens = [w for w in tokens if w not in stop_words
              and w not in CUSTOM_STOPWORDS]                    # remove stopwords
    return " ".join(tokens)
clean["content_clean"] = clean["content_translated"].apply(clean_text)

# -----------------------------
# 6) Remove invalid or empty records to ensure data quality
# -----------------------------
print("\n🔍 Cleaning summary:")
print(f"Rows before cleaning: {len(clean)}")

# 1) Remove missing text rows
clean_missing = clean[clean["url"].isna() | clean["content_raw"].isna()]  # identify missing rows only for url and content
clean.dropna(subset=["url", "content_raw"], inplace=True)
print(f"Removed due to missing text: {len(clean_missing)}") # number of rows removed

# 2) Remove very short titles
removed_short_title = clean[clean["title"].str.len() <= 3]
clean = clean[clean["title"].str.len() > 3]
print(f"Removed due to short titles: {len(removed_short_title)}")

# 3) Remove very short content
removed_short_content = clean[clean["content_raw"].str.len() <= 10]
clean = clean[clean["content_raw"].str.len() > 10]
print(f"Removed due to short content: {len(removed_short_content)}")

print("\n✅ Cleaning finished.\n")

# SHOW EXAMPLES OF REMOVED ROWS
if len(removed_short_title) > 0:
    print("🔎 Example removed short titles:")
    print(removed_short_title[["title", "content_raw"]].head(5), "\n")

if len(removed_short_content) > 0:
    print("🔎 Example removed short content:")
    print(removed_short_content[["title", "content_raw"]].head(5), "\n")

# SHOW SAMPLES OF CLEANED DATA
print(clean.head(3))  # show sample of cleaned data
print(clean[["url", "publisher"]].head(10))  # show sample of URLs and publishers
print(clean["content_raw"].head(3))  # show sample of original content
print(clean["language"].value_counts())  # show language distribution
print(clean["content_translated"].head(3)) #

# -----------------------------
# 8) Save cleaned data into SQLite database
# -----------------------------
conn = sqlite3.connect("db/articles.db")         # create/open database file
clean.to_sql("articles", conn, if_exists="replace", index=False)   # save table
conn.close()

print("✅ ETL complete. Database saved at: db/articles.db")
print(f"Total rows stored: {len(clean)}")
