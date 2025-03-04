import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    uuid TEXT UNIQUE NOT NULL,
    class TEXT,
    email TEXT UNIQUE NOT NULL
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    current_student TEXT,
    publishing TEXT,
    isbn TEXT UNIQUE NOT NULL,
    expiration_date TEXT,
    FOREIGN KEY (current_student) REFERENCES Students(uuid)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS DataLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    student_id INTEGER,
    action TEXT NOT NULL,  -- Borrow or Return
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES Books(id),
    FOREIGN KEY (student_id) REFERENCES Students(id)
);
''')

conn.commit()
conn.close()

print("Database and tables created successfully!")
