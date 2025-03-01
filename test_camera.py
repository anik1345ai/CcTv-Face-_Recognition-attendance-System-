import cv2

def test_camera():
    # Open the default camera (index 0, you can change it to 1 if the first one is not correct)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera. Please check your camera connection.")
        return
    
    print("Camera successfully opened! Press 'q' to exit.")
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        # Display the resulting frame
        cv2.imshow('Test Camera', frame)
        
        # Wait for 'q' to be pressed to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting camera feed...")
            break
    
    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Test the camera
test_camera()
