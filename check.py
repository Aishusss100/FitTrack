import sqlite3

def drop_user_goals_table():
    conn = sqlite3.connect('exercise_progress_with_duration.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            DROP TABLE IF EXISTS user_goals;
        ''')
        conn.commit()
        print("Table 'user_goals' dropped successfully!")
    except Exception as e:
        print(f"Error dropping table: {e}")
    finally:
        conn.close()

# Run the function
if __name__ == "__main__":
    drop_user_goals_table()
