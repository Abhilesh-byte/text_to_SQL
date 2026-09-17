from dotenv import load_dotenv
load_dotenv()  # load all the environment variables

import os
import subprocess

# --- Add this block right after your imports ---
if not os.path.exists("student.db"):
    print("Database not found. Running sql.py to generate it...")
    subprocess.run(["python", "sql.py"])
# -----------------------------------------------
import sqlite3
import google.generativeai as genai

try:
    import streamlit as st
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Streamlit is required to run this app. Install it with: pip install streamlit"
    ) from exc

## Configure the API key (reads GOOGLE_API_KEY from your .env file)
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## (Optional) Uncomment to check which models your API key can access:
# for m in genai.list_models():
#     if 'generateContent' in m.supported_generation_methods:
#         print(m.name)


## Function to load Google Gemini Model and provide sql query as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-3.6-flash')  # updated after 'gemini-2.0-flash' was retired
    response = model.generate_content([prompt, question])
    # Clean up in case the model wraps the query in markdown fences despite instructions
    sql = response.text.strip()
    if sql.startswith("```"):
        sql = sql.strip("`")
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()
    return sql


## Function to retrieve query results from the sql database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows


## Define Your Improved Prompt
prompt = """
You are an expert SQL data analyst. Your task is to convert English questions into valid SQL queries.

### Database Schema
You are working with a SQLite database.
Table Name: STUDENT
Columns:
- NAME (VARCHAR)
- CLASS (VARCHAR)
- SECTION (VARCHAR)
- MARKS (INT)

### Examples
Example 1:
Question: How many total records are present in the database?
SQL: SELECT COUNT(*) FROM STUDENT;

Example 2:
Question: Tell me all the students studying in the Data Science class.
SQL: SELECT * FROM STUDENT WHERE CLASS = 'Data Science';

Example 3:
Question: What is the average mark of students in section A?
SQL: SELECT AVG(MARKS) FROM STUDENT WHERE SECTION = 'A';

### Instructions & Constraints
1. Output ONLY the valid SQL query.
2. Do NOT wrap the SQL code in formatting blocks (e.g., do not use ```sql or ```).
3. Do NOT include any explanations, preambles, or conversational text.
4. Ensure the query is compatible with standard SQLite syntax.
"""

## Function to get column names for the last executed query (for nice table headers)
def read_sql_query_with_columns(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description] if cur.description else []
    conn.commit()
    conn.close()
    return rows, columns


## Streamlit App
st.set_page_config(
    page_title="Text-to-SQL | Gemini Query Agent",
    page_icon="🗃️",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #14152b 0%, #0b0c17 60%);
    }
    .hero {
        padding: 1.5rem 1.75rem;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(99,102,241,0.18), rgba(56,189,248,0.10));
        border: 1px solid rgba(148,163,184,0.15);
        margin-bottom: 1.75rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 1.9rem;
        background: linear-gradient(90deg, #a5b4fc, #67e8f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p {
        margin: 0.35rem 0 0 0;
        color: #94a3b8;
        font-size: 0.95rem;
    }
    .section-label {
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #7dd3fc;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .card {
        background: rgba(30,41,59,0.55);
        border: 1px solid rgba(148,163,184,0.15);
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-bottom: 1.25rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1, #06b6d4);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.55rem 1.4rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        opacity: 0.9;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🗃️ Text-to-SQL Query Agent</h1>
        <p>Ask questions about the STUDENT table in plain English — Gemini converts them into SQL and runs them live.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">Ask a question</div>', unsafe_allow_html=True)
question = st.text_input(
    "Input",
    key="input",
    placeholder="e.g. Show me the top 5 students by marks",
    label_visibility="collapsed",
)
submit = st.button("✨ Generate & Run Query")

# example chips for quick testing
with st.expander("💡 Try an example"):
    st.markdown(
        "- How many total records are present in the database?\n"
        "- Tell me all the students studying in the Data Science class.\n"
        "- What is the average mark of students in section A?"
    )

# if submit is clicked
if submit:
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Asking Gemini and querying the database..."):
            try:
                sql_query = get_gemini_response(question, prompt)
            except Exception as e:
                st.error(f"Gemini request failed: {e}")
                st.stop()

        st.markdown('<div class="section-label">Generated SQL Query</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.code(sql_query, language="sql")
        st.markdown('</div>', unsafe_allow_html=True)

        try:
            rows, columns = read_sql_query_with_columns(sql_query, "student.db")
            st.markdown('<div class="section-label">Result</div>', unsafe_allow_html=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if rows:
                try:
                    import pandas as pd
                    df = pd.DataFrame(rows, columns=columns if columns else None)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                except ImportError:
                    for row in rows:
                        st.write(row)
                st.caption(f"{len(rows)} row(s) returned")
            else:
                st.info("Query ran successfully but returned no results.")
            st.markdown('</div>', unsafe_allow_html=True)
        except sqlite3.Error as e:
            st.error(f"SQL execution error: {e}")