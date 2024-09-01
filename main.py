import streamlit as st
import pdfplumber
import sqlite3
import random
import os

# Database functions
def connect_db():
    conn = sqlite3.connect('questions.db')
    return conn

def create_table(conn):
    conn.execute('''CREATE TABLE IF NOT EXISTS QUESTIONS
           (ID INTEGER PRIMARY KEY AUTOINCREMENT,
           QUESTION TEXT NOT NULL,
           ANSWER TEXT NOT NULL,
           SUBJECT TEXT NOT NULL);''')
    conn.commit()

def insert_question(conn, question, answer, subject):
    conn.execute("INSERT INTO QUESTIONS (QUESTION, ANSWER, SUBJECT) VALUES (?, ?, ?)", 
                 (question, answer, subject))
    conn.commit()

def fetch_questions_by_subject(conn, subject):
    cursor = conn.execute("SELECT QUESTION, ANSWER FROM QUESTIONS WHERE SUBJECT=?", (subject,))
    return cursor.fetchall()

# PDF parsing function using pdfplumber
def extract_questions_answers(pdf_file, subject):
    with pdfplumber.open(pdf_file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    
    questions = []
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip().lower().startswith('q'):
            question = line.strip()
            answer = lines[i + 1].strip() if i + 1 < len(lines) else ''
            questions.append((question, answer))
    
    return questions

# Main Streamlit app
def main():
    st.title("Exam Preparation: Previous Year Papers")
    
    # Connect to the database
    conn = connect_db()
    create_table(conn)
    
    # Upload PDF
    uploaded_file = st.file_uploader("Upload a PDF file with previous year exam papers", type="pdf")
    subject = st.text_input("Enter the subject name for this PDF")
    
    if uploaded_file is not None and subject:
        # Extract questions and answers from the uploaded PDF
        questions = extract_questions_answers(uploaded_file, subject)
        
        if questions:
            st.write(f"PDF successfully processed. {len(questions)} questions extracted.")
            
            # Insert questions into the database
            for question, answer in questions:
                insert_question(conn, question, answer, subject)
            
            st.write("Questions have been saved to the database. You can now take a test.")
            
            # Allow the user to take a test from the saved questions
            if st.button("Start Test"):
                start_test(conn, subject)
                
        else:
            st.write("No questions found in the uploaded PDF.")
    
    # Option to select subject and start test
    st.write("Or choose a subject to start a test:")
    subjects = [row[0] for row in conn.execute("SELECT DISTINCT SUBJECT FROM QUESTIONS").fetchall()]
    
    if subjects:
        selected_subject = st.selectbox("Select Subject", subjects)
        if selected_subject:
            if st.button("Start Test"):
                start_test(conn, selected_subject)

def start_test(conn, subject):
    questions = fetch_questions_by_subject(conn, subject)
    random.shuffle(questions)
    
    score = 0
    for i, (question, correct_answer) in enumerate(questions):
        st.write(f"Q{i + 1}: {question}")
        
        user_answer = st.text_input(f"Your Answer for Q{i + 1}", key=i)
        
        if st.button(f"Submit Answer for Q{i + 1}", key=f"btn_{i}"):
            if user_answer.lower() == correct_answer.lower():
                st.write("Correct!")
                score += 1
            else:
                st.write(f"Wrong! The correct answer is: {correct_answer}")
            
            st.write("---")
    
    st.write(f"Your final score: {score}/{len(questions)}")

if __name__ == "__main__":
    main()
