import sqlite3
import duckdb

# Connect to SQLite
sqlite = sqlite3.connect('db/articles.db')

# Connect to DuckDB (this will create the file if it doesn't exist)
duck = duckdb.connect('db/articles.duckdb')

# Drop existing articles table in DuckDB (if exists)
duck.execute("DROP TABLE IF EXISTS articles;")

# Correct way to copy from SQLite → DuckDB
duck.execute("""
ATTACH 'db/articles.db' AS sqlite_db;
CREATE TABLE articles AS SELECT * FROM sqlite_db.articles;
DETACH sqlite_db;
""")

sqlite.close()
duck.close()

print("✅ Successfully converted SQLite → DuckDB (articles table copied).")
