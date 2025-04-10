import sqlite3

def fetch_user_goals():
    conn = sqlite3.connect('users.db')  
    c = conn.cursor()  

    try:
        
        c.execute('SELECT * FROM users')
        rows = c.fetchall()  

        if rows:
            print("Contents of the user_goals table:")
            for row in rows:
                print(row)
        else:
            print("The user_goals table is empty.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()  


fetch_user_goals()
