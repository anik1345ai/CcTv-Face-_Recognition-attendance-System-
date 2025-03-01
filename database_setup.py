import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup with context management
def initialize_database():
    try:
        with sqlite3.connect('attendance.db') as conn:
            c = conn.cursor()

            # Create tables with enhanced functionality
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                         id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         name TEXT NOT NULL, 
                         designation TEXT NOT NULL, 
                         image_path TEXT NOT NULL)''')

            c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                         id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         user_id INTEGER NOT NULL, 
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                         exit_time DATETIME, 
                         status TEXT CHECK(status IN ('Present', 'Absent', 'Exit')) NOT NULL,
                         FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')

            # Create indexes to improve query performance
            c.execute('''CREATE INDEX IF NOT EXISTS idx_user_id ON attendance(user_id)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_timestamp ON attendance(timestamp)''')

            # Commit changes
            conn.commit()
            logging.info("Database and tables initialized successfully.")

    except sqlite3.Error as e:
        logging.error(f"Error initializing database: {e}")
        raise

# Function to clean up old attendance records (e.g., remove records older than a specific duration)
def clean_up_old_records(duration='6 months'):
    try:
        with sqlite3.connect('attendance.db') as conn:
            c = conn.cursor()

            # Remove records older than the specified duration
            c.execute(f"DELETE FROM attendance WHERE timestamp < datetime('now', '-{duration}')")
            conn.commit()
            logging.info(f"Old attendance records older than {duration} have been removed.")

    except sqlite3.Error as e:
        logging.error(f"Error cleaning up old records: {e}")
        raise

# Main script
if __name__ == "__main__":
    initialize_database()
    
    # Uncomment this line to activate cleanup
    # clean_up_old_records()

    # No need to manually close the connection since 'with' is used.
