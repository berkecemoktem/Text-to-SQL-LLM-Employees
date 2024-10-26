from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sqlite3
import google.generativeai as genai
import pandas as pd


# Configure the Gemini API key
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Function to load Gemini Model and provide SQL query as response
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating SQL query: {e}")
        return None

# Function to retrieve Query from SQL database
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"Error executing SQL query: {e}")
        return []

# Function to save uploaded CSV file to SQLite database
def csv_to_sqlite(csv_file, db_name):
    try:
        df = pd.read_csv(csv_file)
        conn = sqlite3.connect(db_name)
        df.to_sql('UPLOADED_DATA', conn, if_exists='replace', index=False)
        conn.close()
        return df.columns.tolist()
    except Exception as e:
        st.error(f"Error converting CSV to SQLite: {e}")
        return []

# Function to delete the SQLite database file
def delete_database(db_name):
    try:
        if os.path.exists(db_name):
            os.remove(db_name)
    except Exception as e:
        st.error(f"Error deleting database: {e}")

# Streamlit app
st.set_page_config(page_title="Gemini Text to SQL LLM App")
st.header("Gemini App to Retrieve SQL Data (N2SQL)")

# Add a button to navigate to the chatbot pages
st.markdown("Want to chat? [Click here to open the chatbot](Chatbot_UI)")

# File uploader for CSV
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

# Check if a CSV file is uploaded
if uploaded_file is not None:
    db_name = 'uploaded_data.db'
    columns = csv_to_sqlite(uploaded_file, db_name)
    table = 'UPLOADED_DATA'
    st.success("CSV file successfully uploaded and converted to SQLite database.")
else:
    db_name = 'EmployeesFromGithub.db'  # Updated to the correct database
    table = 'emp'  # Updated to the correct table
    columns = ["EMPNO", "ENAME", "JOB", "MGR", "HIREDATE", "SAL", "COMM", "DEPTNO"]  # Updated columns to match your schema

# Define the prompt dynamically based on the columns
prompt = [
    f"""
        You are an expert SQL translator specializing in converting English questions into precise SQL queries.
        The database is named {table}, which includes the following columns: {', '.join(columns)}.
        Your task is to generate an SQL query based solely on the question provided, without using the word 'SQL' or backticks. 
        Ensure your query retrieves relevant data based on the context of the question.

        Here are some example questions:
        - How many employees are there in the {table}? -> SELECT COUNT(*) FROM {table};
        - List all employees who have a salary greater than 3000. -> SELECT * FROM {table} WHERE SAL > 3000;
        - Show me the names of employees who work in the sales department. -> SELECT ENAME FROM {table} WHERE JOB='SALESMAN';
        - What is the average salary of employees in the accounting department? -> SELECT AVG(SAL) FROM {table} WHERE DEPTNO=10;
        - Which employees report to the manager with EMPNO 7839? -> SELECT ENAME FROM {table} WHERE MGR=7839;
        - Which employee is earning the most? -> SELECT ENAME, MAX(SAL) AS HighestSalary FROM {table};

        Ensure your responses are accurate and comprehensive, returning relevant data for the question asked.
        Please provide the SQL query formatted correctly.
    """
]

question = st.text_input("Input your question:", key="input")
submit = st.button("Retrieve")

if submit:
    response = get_gemini_response(question, prompt)
    if response:
        st.subheader("The SQL Query Generated is:")
        st.code(response, language='sql')

        data = read_sql_query(response, db_name)
        if data:
            st.subheader("The response is:")
            for row in data:
                st.write(row)
        else:
            st.write("No data found or an error occurred.")

    # Delete the uploaded database after the task is completed
    if uploaded_file is not None:
        delete_database(db_name)
