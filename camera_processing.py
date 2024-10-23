import cv2
import numpy as np

# OpenCV setup
cap = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Define color range for segmentation (adjust for your cellphone color)
lower_blue = np.array([100, 150, 0])  # Lower bound for HSV (example: baby blue)
upper_blue = np.array([140, 255, 255])  # Upper bound for HSV

lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Function to process the webcam input
def process_frame():
    ret, frame = cap.read()
    if not ret:
        return None

    # Flip frame to avoid mirrored view
    frame = cv2.flip(frame, 1)

    # Convert frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create mask for blue
    mask_blue = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    # Create two masks for red color
    mask_red1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)

    # Combine the two red masks
    mask_red = mask_red1 + mask_red2

    # Combine blue and red masks
    mask = mask_blue + mask_red

    # Find contours of the object
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Show the frame and the mask (for debugging purposes)
    cv2.imshow('Webcam', frame)  # Show the actual camera feed
    cv2.imshow('Mask', mask)  # Show the mask after segmentation

    # Find the largest contour by area (assuming it's the object of interest)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            # Calculate the center of the object
            cx = int(M["m10"] / M["m00"])
            print(f"Object X Coordinate: {cx}")  # Print x-coordinate for debugging
            return cx  # Return x-coordinate of the object's center

    return None

def release_camera():
    cap.release()
    cv2.destroyAllWindows()