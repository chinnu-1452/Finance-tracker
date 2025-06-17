import sqlite3
import hashlib

# Initialize DB & tables
def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            category TEXT,
            amount REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

def login_user(username, password):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    data = cursor.fetchone()
    conn.close()
    return data

def get_user_id(username):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    conn.close()
    return user_id[0] if user_id else None

def add_expense(user_id, date, category, amount):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (user_id, date, category, amount) VALUES (?, ?, ?, ?)",
                   (user_id, date, category, amount))
    conn.commit()
    conn.close()

def get_expenses(user_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, category, amount FROM expenses WHERE user_id = ? ORDER BY date ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# 🆕 CRUD UPDATE
def update_expense(expense_id, date, category, amount):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE expenses SET date = ?, category = ?, amount = ? WHERE id = ?",
                   (date, category, amount, expense_id))
    conn.commit()
    conn.close()

# 🆕 CRUD DELETE
def delete_expense(expense_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
