import sqlite3

def fetch_progress_data():
    conn = sqlite3.connect('exercise_progress_with_duration.db')
    cursor = conn.cursor()

    query = """
    SELECT * FROM exercise_progress_with_duration
    WHERE username = 'admin' AND date = '2025-03-19';
    """
    cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()

    if rows:
        for row in rows:
            print(row)
    else:
        print("No data found for the specified username and date.")

fetch_progress_data()
