import streamlit as st
import sqlite3
import google.generativeai as genai
import os

# Configure the API key for Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Function to get SQL query from Gemini
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])
        return response.text.strip()
    except Exception as e:
        st.error(f"Error generating SQL query: {e}")
        return None

# Function to read the result of SQL query from SQLite database
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

# Function to save feedback to a text file
def save_feedback(feedback):
    feedback_file = "feedback.txt"
    try:
        with open(feedback_file, mode='a') as file:
            file.write(f"{feedback}\n")  # Save feedback in a new line
            st.success("Feedback saved successfully!")
    except Exception as e:
        st.error(f"Error saving feedback: {e}")

# Define prompt for Gemini
columns = ["EMPNO", "ENAME", "JOB", "MGR", "HIREDATE", "SAL", "COMM", "DEPTNO"]
table = 'emp'
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

# Streamlit Chat UI
st.title("Chatbot UI")
st.write("Ask me questions about the employee database!")

# css
st.markdown(
    """
    <style>
    .stApp {
        background-color: #79d1c3;
    }
    .st-header h2 {
        font-size: 40px;  # Adjust the font size as needed
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Input text from the user
user_input = st.text_input("You:", key="user_input")
if st.button("Send", type="primary"):
    # Generate SQL query from the Gemini API
    if user_input:
        sql_query = get_gemini_response(user_input, prompt)
        if sql_query:
            st.write(f"Bot (SQL Query): {sql_query}")
            # Execute the query and display the results
            results = read_sql_query(sql_query, "EmployeesFromGithub.db")
            if results:
                st.write("Bot (Response):")
                for row in results:
                    st.write(row)
            else:
                st.write("No data found.")

            # Feedback section with buttons
            st.write("Was this response helpful?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Good"):
                    save_feedback("Good")
            with col2:
                if st.button("Bad"):
                    save_feedback("Bad")