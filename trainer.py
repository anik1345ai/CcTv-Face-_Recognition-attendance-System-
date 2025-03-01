import cv2
import numpy as np
import os
import sqlite3

# Database setup
conn = sqlite3.connect('attendance.db')
c = conn.cursor()

# Load pre-trained face detector
face_cascade_path = 'haarcascade_frontalface_default.xml'
if not os.path.exists(face_cascade_path):
    print(f"Error: '{face_cascade_path}' not found!")
    exit()

face_cascade = cv2.CascadeClassifier(face_cascade_path)

recognizer = cv2.face.LBPHFaceRecognizer_create()

# Prepare training data
def get_images_and_labels(image_dir='images'):
    # Check if image directory exists
    if not os.path.exists(image_dir):
        print(f"Error: Directory '{image_dir}' not found!")
        exit()

    image_paths = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if len(image_paths) == 0:
        print("No images found in the 'images' directory.")
        return [], []

    face_samples = []
    ids = []
    user_id = 1  # Starting ID for user images
    
    for image_path in image_paths:
        gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if gray is None:
            print(f"Warning: Unable to read image {image_path}. Skipping.")
            continue

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray)
        if len(faces) == 0:
            print(f"Warning: No face detected in {image_path}. Skipping.")
            continue

        # Crop faces and add to the dataset
        for (x, y, w, h) in faces:
            face_samples.append(gray[y:y+h, x:x+w])
            ids.append(user_id)
        
        user_id += 1  # Increment ID for the next user image

    return face_samples, ids

# Training
def train_model():
    try:
        faces, ids = get_images_and_labels()

        if len(faces) == 0:
            print("Error: No valid faces found in the dataset.")
            return

        print(f"Training with {len(faces)} faces...")
        recognizer.train(faces, np.array(ids))
        
        # Save the trained model
        trainer_file = 'trainer.yml'
        recognizer.write(trainer_file)  # Save the trained model
        print(f"Training completed successfully. Model saved to '{trainer_file}'.")
    except Exception as e:
        print(f"Error during training: {e}")
    finally:
        conn.close()  # Ensure the database connection is closed even if an error occurs

if __name__ == "__main__":
    # Execute training
    train_model()
