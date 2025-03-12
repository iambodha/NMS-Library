import sqlite3
from typing import List, Tuple, Optional, Dict

# Utility function to get a database connection
# Make sure "library.db" is accessible in the current directory.

def get_connection(db_name: str = "library.db") -> sqlite3.Connection:
    return sqlite3.connect(db_name)

# --------------------------------
# STUDENT FUNCTIONS
# --------------------------------

def add_student(full_name: str, uuid: str, student_class: str, email: str) -> None:
    """Adds a new student entry to the Students table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Students (full_name, uuid, class, email)
        VALUES (?, ?, ?, ?)
        """,
        (full_name, uuid, student_class, email)
    )
    conn.commit()
    conn.close()


def update_student(student_id: int, full_name: Optional[str] = None,
                   uuid: Optional[str] = None,
                   student_class: Optional[str] = None,
                   email: Optional[str] = None) -> None:
    """Updates student data for a given student_id."""
    # Build an SQL query dynamically based on which fields are provided
    fields_to_update = []
    params = []

    if full_name is not None:
        fields_to_update.append("full_name = ?")
        params.append(full_name)
    if uuid is not None:
        fields_to_update.append("uuid = ?")
        params.append(uuid)
    if student_class is not None:
        fields_to_update.append("class = ?")
        params.append(student_class)
    if email is not None:
        fields_to_update.append("email = ?")
        params.append(email)

    if not fields_to_update:
        return  # Nothing to update

    params.append(student_id)
    set_clause = ", ".join(fields_to_update)

    query = f"UPDATE Students SET {set_clause} WHERE id = ?"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()


def delete_student(student_id: int) -> None:
    """Deletes a student from the Students table by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


def get_students() -> List[Tuple]:
    """Returns all students."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Students")
    results = cursor.fetchall()
    conn.close()
    return results

def search_student(student_id: Optional[int] = None, uuid: Optional[str] = None, full_name: Optional[str] = None) -> Optional[Dict[str, any]]:
    """Searches for a student based on id, uuid, or full_name."""
    if not any([student_id, uuid, full_name]):
        raise ValueError("At least one search parameter must be provided")

    query = "SELECT * FROM Students WHERE "
    params = []

    conditions = []
    if student_id is not None:
        conditions.append("id = ?")
        params.append(student_id)
    if uuid is not None:
        conditions.append("uuid = ?")
        params.append(uuid)
    if full_name is not None:
        conditions.append("full_name = ?")
        params.append(full_name)

    query += " OR ".join(conditions)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return None

    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, result))

# --------------------------------
# BOOK FUNCTIONS
# --------------------------------

def add_book(title: str, author: str, publishing: str, isbn: str) -> None:
    """Adds a new book to the Books table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Books (title, author, publishing, isbn)
        VALUES (?, ?, ?, ?)""",
        (title, author, publishing, isbn)
    )
    conn.commit()
    conn.close()


def update_book(book_id: int, title: Optional[str] = None,
                 author: Optional[str] = None,
                 current_student: Optional[str] = None,
                 publishing: Optional[str] = None,
                 isbn: Optional[str] = None,
                 expiration_date: Optional[str] = None) -> None:
    """Updates the book data for a given book_id."""
    fields_to_update = []
    params = []

    if title is not None:
        fields_to_update.append("title = ?")
        params.append(title)
    if author is not None:
        fields_to_update.append("author = ?")
        params.append(author)
    if current_student is not None:
        fields_to_update.append("current_student = ?")
        params.append(current_student)
    if publishing is not None:
        fields_to_update.append("publishing = ?")
        params.append(publishing)
    if isbn is not None:
        fields_to_update.append("isbn = ?")
        params.append(isbn)
    if expiration_date is not None:
        fields_to_update.append("expiration_date = ?")
        params.append(expiration_date)

    if not fields_to_update:
        return  # Nothing to update

    params.append(book_id)
    set_clause = ", ".join(fields_to_update)

    query = f"UPDATE Books SET {set_clause} WHERE id = ?"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()


def delete_book(book_id: int) -> None:
    """Deletes a book from the Books table by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()


def get_books() -> List[Tuple]:
    """Returns all books."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Books")
    results = cursor.fetchall()
    conn.close()
    return results

# --------------------------------
# DATA LOG FUNCTIONS
# --------------------------------

def log_action(book_id: int, student_id: int, action: str) -> None:
    """Logs a borrow or return action in the DataLog."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO DataLog (book_id, student_id, action)
            VALUES (?, ?, ?)""",
            (book_id, student_id, action)
        )
        conn.commit()
    except Exception as e:
        print(f"Failed to log action: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_log_entries() -> List[Tuple]:
    """Returns all log entries from the DataLog."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM DataLog")
    results = cursor.fetchall()
    conn.close()
    return results

# --------------------------------
# BORROW AND RETURN BOOK FUNCTIONS
# --------------------------------

def borrow_book(book_id: int, student_uuid: str, expiration_date: str) -> None:
    """Handles borrowing a book by setting the current student and updating the expiration date."""
    conn = get_connection()
    cursor = conn.cursor()

    # Retrieve student ID from uuid
    cursor.execute("SELECT id FROM Students WHERE uuid = ?", (student_uuid,))
    student_row = cursor.fetchone()
    if not student_row:
        raise ValueError("No student found with the given UUID.")
    student_id = student_row[0]

    # Update book record
    cursor.execute(
        "UPDATE Books SET current_student = ?, expiration_date = ? WHERE id = ?",
        (student_uuid, expiration_date, book_id)
    )

    # Log the borrow action
    log_action(book_id, student_id, "Borrow")

    conn.commit()
    conn.close()


def return_book(book_id: int) -> None:
    """Handles returning a book by clearing current_student and expiration_date."""
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch current student to log
    cursor.execute("SELECT current_student FROM Books WHERE id = ?", (book_id,))
    student_uuid = cursor.fetchone()
    if not student_uuid or not student_uuid[0]:
        raise ValueError("This book doesn't seem to be borrowed.")
    student_uuid = student_uuid[0]

    # Retrieve student ID from uuid
    cursor.execute("SELECT id FROM Students WHERE uuid = ?", (student_uuid,))
    student_row = cursor.fetchone()
    if not student_row:
        raise ValueError("No student found with the given UUID.")
    student_id = student_row[0]

    # Update book record
    cursor.execute(
        "UPDATE Books SET current_student = NULL, expiration_date = NULL WHERE id = ?",
        (book_id,)
    )

    # Log the return action
    log_action(book_id, student_id, "Return")

    conn.commit()
    conn.close()

# --------------------------------
# SAMPLE USAGE (optional)
# --------------------------------

def main():
    # Example usage of the functions in this script
    print("Adding a student...")
    add_student("John Doe", "uuid-123", "Class A", "john@example.com")

    print("Adding a book...")
    add_book("A Great Book", "Alice Smith", "PublishCorp", "isbn-456")

    print("Borrowing a book...")
    # Let's assume book with ID=1 is the one we just added,
    # and it corresponds to "isbn-456"
    borrow_book(book_id=1, student_uuid="uuid-123", expiration_date="2023-12-31")

    print("Returning a book...")
    return_book(book_id=1)

    print("All students:", get_students())
    print("All books:", get_books())
    print("All logs:", get_log_entries())

if __name__ == "__main__":
    print(search_student(1))


# Search a Book