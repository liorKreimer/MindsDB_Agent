import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join("db", "articles.db")

def test_db_exists():
    """Database file should exist after ETL runs."""
    assert os.path.exists(DB_PATH), "articles.db was not created. Run ETL first."

def test_articles_table_exists():
    """The articles table should exist inside the database."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles';")
    result = cur.fetchone()
    con.close()
    assert result is not None, "Table 'articles' does not exist in database."

def test_required_columns_present():
    """The table must contain the columns the project requires."""
    required = {
        "pub_date",
        "url",
        "publisher",
        "title",
        "content_raw",
        "language",
        "content_translated",
        "content_clean"
    }

    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("PRAGMA table_info(articles);", con)
    con.close()

    cols = set(df["name"])
    missing = required - cols
    assert not missing, f"Missing required columns: {missing}"

def test_non_empty_content():
    """Verify the dataset is not empty and contains meaningful text."""
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT content_clean FROM articles LIMIT 200;", con)
    con.close()

    assert len(df) > 0, "articles table appears empty."
    assert df["content_clean"].str.len().mean() > 20, "content_clean looks empty or unprocessed."
