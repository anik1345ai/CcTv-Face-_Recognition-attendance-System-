import cv2
import sqlite3
import datetime
import numpy as np
import logging
import os
import time
from mtcnn import MTCNN

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection
def get_db_connection():
    conn = sqlite3.connect('attendance.db', check_same_thread=False)
    return conn, conn.cursor()

conn, c = get_db_connection()

# Load LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
trainer_file = "trainer.yml"

if os.path.exists(trainer_file):
    recognizer.read(trainer_file)
    logging.info("✅ LBPH Face Recognizer model loaded successfully.")
else:
    logging.error(f"❌ Face recognizer model '{trainer_file}' not found! Train the model first.")
    exit()

# Initialize MTCNN face detector
detector = MTCNN()

# Function to mark attendance with better handling
def mark_attendance(user_id, status):
    now = datetime.datetime.now()
    try:
        c.execute("SELECT timestamp FROM attendance WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
        last_attendance = c.fetchone()

        if last_attendance:
            last_time = datetime.datetime.strptime(last_attendance[0], '%Y-%m-%d %H:%M:%S.%f')
            if (now - last_time).seconds < 300:  # Prevent duplicate marking within 5 minutes
                logging.info(f"⚠️ User {user_id} already marked recently. Skipping entry.")
                return

        c.execute("INSERT INTO attendance (user_id, timestamp, status) VALUES (?, ?, ?)", (user_id, now, status))
        conn.commit()
        logging.info(f"✅ Attendance marked: User ID = {user_id}, Status = {status}")

    except sqlite3.Error as e:
        logging.error(f"❌ Database error: {e}")

# Function for face tracking and recognition
def recognize_face_and_mark_attendance(frame):
    # Detect faces using MTCNN
    faces = detector.detect_faces(frame)

    for face in faces:
        x, y, w, h = face['box']

        # Process the detected face (e.g., convert to grayscale and apply recognition)
        face = frame[y:y+h, x:x+w]

        # Convert face to grayscale and preprocess
        gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        gray_face = cv2.resize(gray_face, (100, 100))  # Ensure correct size
        gray_face = cv2.equalizeHist(gray_face)  # Improve contrast

        try:
            id_, conf = recognizer.predict(gray_face)
            logging.info(f"👤 Detected face ID: {id_}, Confidence: {conf}")

            if conf < 70:  # Stricter confidence threshold
                c.execute("SELECT id, name FROM users WHERE id = ?", (id_,))
                user = c.fetchone()

                if user:
                    user_id, name = user
                    mark_attendance(user_id, 'Present')

                    # Draw rectangle and label for known person
                    cv2.putText(frame, f"{name} (ID:{user_id})", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                else:
                    # Draw rectangle and label for unknown person
                    cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    logging.warning("⚠️ Unknown face detected!")
            else:
                # Draw rectangle and label for unknown person
                cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

        except Exception as e:
            logging.error(f"❌ Error during face recognition: {e}")

    return frame

# Capture video from CCTV camera
camera_url = 'rtsp://rstp_admin:rstp_12345-admin@10.100.93.108:554/cam/realmonitor?channel=16&subtype=0'  # Replace with actual URL

cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)  # Use FFMPEG for RTSP stability
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Set a higher resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Set a higher resolution
cap.set(cv2.CAP_PROP_FPS, 15)  # Reduce FPS for better performance

if not cap.isOpened():
    logging.error("❌ Error: Could not open camera feed")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        logging.error("❌ Error: Could not read frame from camera")
        time.sleep(2)  # Wait before retrying
        continue

    frame = recognize_face_and_mark_attendance(frame)
    cv2.imshow('🔴 CCTV Camera Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
conn.close()
