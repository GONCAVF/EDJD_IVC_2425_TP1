import cv2
import numpy as np

# OpenCV setup
cap = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Define color range for segmentation (adjust for green color)
lower_green = np.array([35, 100, 100])  # Lower bound for HSV (example for green)
upper_green = np.array([85, 255, 255])  # Upper bound for HSV

lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Function to process the webcam input and show segmentation result
def process_frame():
    ret, frame = cap.read()
    if not ret:
        return None, None

    # Flip frame to avoid mirrored view
    frame = cv2.flip(frame, 1)

    # Convert frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create mask for green
    mask_green = cv2.inRange(hsv_frame, lower_green, upper_green)

    # Create two masks for red color
    mask_red1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)

    # Combine the two red masks
    mask_red = mask_red1 + mask_red2

    # Combine green and red masks
    mask = mask_green + mask_red

    # Show the original frame and the combined mask
    cv2.imshow('Webcam', frame)  # Original webcam feed
    cv2.imshow('Mask', mask)     # Mask window already implemented

    # New window to show the segmentation result
    segmentation_result = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imshow('Segmentation Result', segmentation_result)  # Shows only detected colors

    # Find contours of the object
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    object_x = None  # Default to None if no object is detected

    # Find the largest contour by area (assuming it's the object of interest)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] > 0:
            # Calculate the center of the object
            cx = int(M["m10"] / M["m00"])
            object_x = cx  # X-coordinate of the object's center

    return object_x, mask  # Return x-coordinate and the mask for additional processing

def release_camera():
    cap.release()
    cv2.destroyAllWindows()