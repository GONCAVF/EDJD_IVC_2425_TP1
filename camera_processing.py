import cv2
import numpy as np

# OpenCV setup
cap = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Color range for segmentation
lower_green = np.array([35, 100, 100])
upper_green = np.array([85, 255, 255])

lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

# Function to process the webcam input and show segmentation result
def process_frame():
    ret, frame = cap.read()
    if not ret:
        return None, None

    frame = cv2.flip(frame, 1)

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create masks for red and green colors
    mask_green = cv2.inRange(hsv_frame, lower_green, upper_green)

    mask_red1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)

    # Combine masks
    mask_red = mask_red1 + mask_red2

    # contours
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Largest contour for red and green
    object_x_red = None
    object_x_green = None

    # x-coordinate for the red object
    if contours_red:
        largest_contour_red = max(contours_red, key=cv2.contourArea)
        if cv2.contourArea(largest_contour_red) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour_red)
            object_x_red = x + (w // 2)

    # x-coordinate for the green object
    if contours_green:
        largest_contour_green = max(contours_green, key=cv2.contourArea)
        if cv2.contourArea(largest_contour_green) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour_green)
            object_x_green = x + (w // 2)

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask Red", mask_red)
    cv2.imshow("Mask Green", mask_green)

    return object_x_red, object_x_green

def release_camera():
    cap.release()
    cv2.destroyAllWindows()