import sqlite3
import json
from datetime import datetime

DB_NAME = "chat_history.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        role TEXT,
        message TEXT,
        sources TEXT,
        timestamp TEXT,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    )
    """)

    conn.commit()
    conn.close()


def create_conversation():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO conversations (created_at) VALUES (?)",
        (datetime.now().isoformat(),)
    )

    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return conversation_id


def save_message(conversation_id, role, message, sources=None):
    conn = get_connection()
    cursor = conn.cursor()

    if sources:
        formatted_sources = json.dumps(sources)
    else:
        formatted_sources = None

    cursor.execute(
        """
        INSERT INTO messages (conversation_id, role, message, sources, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            conversation_id,
            role,
            message,
            formatted_sources,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def delete_conversation(convo_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM messages WHERE conversation_id=?", (convo_id,))
    cursor.execute("DELETE FROM conversations WHERE id=?", (convo_id,))

    conn.commit()
    conn.close()


def load_conversations():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        c.id,
        c.created_at,
        (
            SELECT message 
            FROM messages 
            WHERE conversation_id = c.id AND role='user'
            ORDER BY id ASC 
            LIMIT 1
        ) as first_message
    FROM conversations c
    ORDER BY c.id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    conversations = []

    for convo_id, created_at, first_message in rows:

        if first_message:
            words = first_message.split()
            preview = " ".join(words[:5])
            if len(words) > 5:
                preview += "..."
        else:
            preview = "New Conversation"

        conversations.append({
            "id": convo_id,
            "created_at": created_at,
            "title": preview
        })

    return conversations


def load_messages(conversation_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, message, sources, timestamp
    FROM messages
    WHERE conversation_id=?
    ORDER BY id
    """, (conversation_id,))

    rows = cursor.fetchall()
    conn.close()

    messages = []

    for role, message, sources, timestamp in rows:
        messages.append({
            "role": role,
            "msg": message,
            "sources": json.loads(sources) if sources else [],
            "timestamp": timestamp
        })

    return messages