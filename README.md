This project performs **OSINT-style analysis** on defense-related news articles.  
It includes:

- **ETL Pipeline** → Loads + cleans + normalizes article text  
- **Language Detection + Translation** for non-English articles  
- **DuckDB / SQLite database** for structured storage  
- **Streamlit Dashboard** to explore and visualize insights  
- **MindsDB AI Agent** that answers natural-language questions **using only the dataset**  

---

## 1) 🔧 Environment Setup
#### Create virtual environment

python -m venv .venv

#### Activate environment (Windows)

 .\.venv\Scripts\activate

#### Install dependencies 

pip install -r requirements.txt

#### The raw dataset used in this project is provided in the repository at:

data/datanalystexam.csv

## 2) 🏗 Run ETL (Clean and Prepare Articles)

python etl/load_to_sqlite.py

## 3) Convert SQLite → DuckDB (Required for MindsDB)

python SQLlite_To_Duckdb.py

## 4) 🧪 Tests

#### Run:

pytest -q

## 5) 🗄 Database Schema check

python SQL_creation.py

## 6) 📊 Run the Analytical Dashboard

streamlit run dashboard/app.py

## 7) 🧠 MindsDB - AI Agent for Natural Language Querying 

##### Start MindsDB using Docker 

cd mindsdb_local

docker compose up -d

Open UI →
http://localhost:47334

---

##### Create Database Connection in MindsDB

###### Paste into MindsDB SQL Editor:

CREATE DATABASE articles_db

WITH ENGINE = "duckdb"

PARAMETERS = {

  "database": "/mnt/data/articles.duckdb"
  
};

---
##### Create the AI Agent

###### Paste into MindsDB SQL Editor:

CREATE AGENT defense_insights

USING

  model = {
  
    "provider": "google",
    
    "model_name": "gemini-2.5-flash", # add google API Key 
    
    "api_key": "{{GEMINI_API_KEY}}"
    
  },
  
  data = {
  
    "tables": ["articles_db.articles"]
    
  },
  
  prompt_template = 'You are an OSINT defense analyst.
  
Use only the articles table. Retrieve and synthesize insights.

If the answer is not supported,

reply: "I cannot answer this based on the available articles."';

---

##### Ask questions the Agent:
###### Paste into MindsDB SQL Editor:

SELECT *

FROM defense_insights

WHERE question = 'Which publisher appears most frequently?';


##### Or ask in the Agent chat tab
---













