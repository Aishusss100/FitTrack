import sqlite3

def view_exercise_data():
    conn = sqlite3.connect('exercise_progress_with_duration.db')
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM exercise_progress_with_duration WHERE username = 'admin' ORDER BY date DESC LIMIT 50")
        rows = c.fetchall()
        if rows:
            print("Recent exercise data for 'admin':")
            for row in rows:
                print(row)
        else:
            print("No data found for 'admin'.")
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")
    finally:
        conn.close()

view_exercise_data()
