# MindsDB_Agent — Defense Article Analytics & Natural Language Querying

This project loads a large news article dataset, performs text cleaning and language normalization, stores the cleaned dataset in a database, provides an interactive analytical dashboard, and enables natural-language querying using a MindsDB AI Agent connected to a vector-search enhanced DuckDB database.

The project simulates a real OSINT (Open-Source Intelligence) workflow:
- Data ingestion + cleaning
- Text normalization & stopword filtering
- Keyword analytics and topic patterns
- Dashboard-based exploration
- AI agent answering questions *only using the dataset*

---

## 1) 🔧 Environment Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python -m nltk.downloader stopwords

2) 🏗 Run ETL to Create SQLite Database
python etl/load_to_sqlite.py

Step	Description
1	Loads original CSV (data/datanalystexam.csv)
2	Extracts publisher from URL
3	Detects article language
4	Translates non-English articles (optional)
5	Cleans text: lowercase + remove stopwords + strip noise
6	Saves final dataset to db/articles.db

Convert SQLite → DuckDB (Required for MindsDB)
MindsDB works most reliably with DuckDB.

python SQLlite_To_Duckdb.py

4) 📊 Run the Analytical Dashboard
streamlit run dashboard/app.py

The dashboard includes:
Explore Articles (search + filters)
Articles per Publisher
Articles Over Time
Language Distribution
Keyword Frequency Per Publisher
Tag Cloud (using cleaned text)

5) 🧠 MindsDB — AI Agent for Natural Language Querying
Start MindsDB Server (Docker)
cd mindsdb_local
docker compose up -d

Open UI →
http://localhost:47334

Create Database Connection in MindsDB
Paste into MindsDB SQL Editor:

CREATE DATABASE articles_db
WITH ENGINE = "duckdb"
PARAMETERS = {
  "database": "/mnt/data/articles.duckdb"
};

Create the AI Agent
CREATE AGENT defense_insights
USING
  model = {
    "provider": "google",
    "model_name": "gemini-2.5-flash",
    "api_key": "{{GEMINI_API_KEY}}"
  },
  data = {
    "tables": ["articles_db.articles"]
  },
  prompt_template = 'You are an OSINT defense analyst.
Use only the articles table. Retrieve and synthesize insights.
If the answer is not supported,
reply: "I cannot answer this based on the available articles."';

Ask questions:
SELECT *
FROM defense_insights
WHERE question = 'Which publisher appears most frequently?';
Or in the Agent chat

6) 🧪 Tests
Run:

pytest -q

Tests validate:
Database exists
Table exists
Required columns are present
Clean text is non-empty

7) 🗄 Database Schema
python SQL_creation.py











