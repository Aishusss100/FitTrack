import sqlite3

def read_user_table():
    try:
        # Step 1: Connect to the SQLite database
        conn = sqlite3.connect('users.db')  # Replace 'users.db' with your database name
        print("Connected to the database successfully")

        # Step 2: Create a cursor object
        cursor = conn.cursor()

        # Step 3: Write and execute the SQL query
        cursor.execute("SELECT * FROM users")  # Replace 'user' with your table name

        # Step 4: Fetch all rows from the table
        rows = cursor.fetchall()

        # Step 5: Display the rows
        print("Contents of the 'users' table:")
        for row in rows:
            print(row)

    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
    finally:
        # Step 6: Close the connection
        if conn:
            conn.close()
            print("Database connection closed")

# Call the function
read_user_table()
