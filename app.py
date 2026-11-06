
import streamlit as st
import pandas as pd
import re
import sqlite3

st.set_page_config(
    page_title="AI Comment Moderator",
    page_icon="🛡️"
)

# Database connection
def create_database():
    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment TEXT NOT NULL,
            result TEXT,
            detected_words TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

# Save comment
def save_comment(comment, result, words):
    conn = sqlite3.connect("comments.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO comments (comment, result, detected_words) VALUES (?, ?, ?)",
        (comment, result, ", ".join(words))
    )

    conn.commit()
    conn.close()

create_database()

st.title("🛡️ AI Comment Moderator")
st.subheader("Detect harmful and inappropriate comments")

bad_words = [
    "stupid", "idiot", "hate", "fool",
    "kill", "abuse", "moron", "useless","hurt","threat","attack","harm"
]

def moderate_comment(comment):
    words = re.findall(r'\b\w+\b', comment.lower())
    found_words = [word for word in words if word in bad_words]

    if found_words:
        return "Harmful Comment", found_words
    return "Safe Comment", []

comment = st.text_area("Enter your comment:")

if st.button("Analyze Comment"):

    if comment.strip():

        result, detected_words = moderate_comment(comment)

        save_comment(comment, result, detected_words)

        if result == "Harmful Comment":
            st.error("⚠️ " + result)
            st.write("Detected words:", ", ".join(detected_words))
        else:
            st.success("✅ " + result)

        st.write("Original Comment:", comment)
        st.success("Comment saved in database!")

    else:
        st.warning("Please enter a comment first.")

# Dashboard
st.subheader("📊 Dashboard")

conn = sqlite3.connect("comments.db")

df = pd.read_sql_query(
    "SELECT * FROM comments ORDER BY id DESC", conn
)

conn.close()

total_comments = len(df)

harmful_comments = df["result"].astype(str).str.contains(
    "Harmful", case=False
).sum()

safe_comments = df["result"].astype(str).str.contains(
    "Safe", case=False
).sum()

col1, col2, col3 = st.columns(3)

col1.metric("Total Comments", total_comments)
col2.metric("Safe Comments", safe_comments)
col3.metric("Harmful Comments", harmful_comments)

# Display saved comments
st.subheader("📋 Saved Comments")

st.dataframe(df, width="stretch")

st.caption("AI Comment Moderator - Project Demo")