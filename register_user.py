import cv2
import os
import sqlite3
import uuid

# Database setup
conn = sqlite3.connect('attendance.db')
c = conn.cursor()

# Create a table for storing user data if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    designation TEXT,
    image_path TEXT
)''')
conn.commit()

# Directory to store user images
image_dir = "images"
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# Function to register a new user
def register_user(name, designation):
    # Validate inputs
    if not name or not designation:
        print("Error: Name and designation cannot be empty!")
        return

    # Open the webcam
    cap = cv2.VideoCapture(0)  # Using default camera
    
    if not cap.isOpened():
        print("Error: Could not access the webcam. Please check your camera connection.")
        return
    
    print("Capturing image... Please look at the camera.")
    
    user_id = None
    image_path = ""
    
    # Capture an image of the user
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame. Please try again.")
            break
        
        # Display the captured frame
        cv2.imshow('Registering User', frame)
        
        # Wait for the user to press 'q' to take the picture
        print("Press 'q' to capture your image.")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Generate a unique filename using UUID
            image_filename = f"{uuid.uuid4().hex}.jpg"
            image_path = os.path.join(image_dir, image_filename)
            
            # Save the image to a file
            cv2.imwrite(image_path, frame)  # Save the captured image
            print(f"Image saved as {image_path}")
            break
    
    # Release the webcam and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

    # Insert user details into the database
    try:
        # Get the next available user ID
        c.execute("SELECT MAX(id) FROM users")
        max_id = c.fetchone()[0]
        user_id = max_id + 1 if max_id else 1
        
        # Insert the user data
        c.execute("INSERT INTO users (id, name, designation, image_path) VALUES (?, ?, ?, ?)",
                  (user_id, name, designation, image_path))
        conn.commit()
        
        print(f"User '{name}' registered with ID {user_id}.")
        print(f"User {name}'s details are saved, and their image is stored at {image_path}.")
        
    except sqlite3.Error as e:
        print(f"Error with database operation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Main script
if __name__ == "__main__":
    print("Welcome to the User Registration System!")
    
    # Input validation and user-friendly prompts
    name = input("Enter your full name (e.g., John Doe): ").strip()
    designation = input("Enter your designation (e.g., Developer, Manager): ").strip()
    
    # Ensure valid input
    if not name or not designation:
        print("Error: Name and designation are required. Please try again.")
    else:
        register_user(name, designation)
    
    # Close the database connection
    conn.close()
