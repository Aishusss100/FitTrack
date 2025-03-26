import sqlite3

def fetch_user_goals():
    conn = sqlite3.connect('exercise_progress_with_duration.db')  # Connect to the database
    c = conn.cursor()  # Create a cursor object

    try:
        # Execute a query to fetch all the contents of the table
        c.execute('SELECT * FROM user_goals')
        rows = c.fetchall()  # Fetch all rows from the executed query

        if rows:
            print("Contents of the user_goals table:")
            for row in rows:
                print(row)
        else:
            print("The user_goals table is empty.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()  # Close the database connection

# Call the function
fetch_user_goals()
