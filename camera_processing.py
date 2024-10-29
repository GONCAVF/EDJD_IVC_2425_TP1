import cv2
import numpy as np

# OpenCV setup
cam = cv2.VideoCapture(0)
cam2 = cv2.VideoCapture(1)

# Check if the camera is opened correctly
if not cam.isOpened() or not cam2.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Color range for segmentation
lower_green = np.array([35, 100, 100])
upper_green = np.array([85, 255, 255])

lower_red1 = np.array([0, 120, 70])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 120, 70])
upper_red2 = np.array([180, 255, 255])

lower_blue = np.array([100, 150, 50])
upper_blue = np.array([140, 255, 255])

# Function to process the webcam input and show segmentation result
def process_frame():
    ret, frame = cam.read()
    ret2, frame2 = cam2.read()
    if not ret or not ret2:
        return None, None

    frame = cv2.flip(frame, 1)
    # frame2 = cv2.flip(frame2, 1)

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv_frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)

    # Create masks for red and green colors frame
    mask_green = cv2.inRange(hsv_frame, lower_green, upper_green)

    mask_blue = cv2.inRange(hsv_frame, lower_blue, upper_blue)

    mask_red1 = cv2.inRange(hsv_frame, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv_frame, lower_red2, upper_red2)

    # Create masks for red and green colors frame2
    mask_green2 = cv2.inRange(hsv_frame2, lower_green, upper_green)

    mask_blue2 = cv2.inRange(hsv_frame2, lower_blue, upper_blue)

    mask_red12 = cv2.inRange(hsv_frame2, lower_red1, upper_red1)
    mask_red22 = cv2.inRange(hsv_frame2, lower_red2, upper_red2)

    # Combine masks frame
    mask_red = mask_red1 + mask_red2

    # Combine masks frame2
    mask_red2 = mask_red12 + mask_red22

    # contours frame
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue , _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # contours frame2
    contours_green2, _ = cv2.findContours(mask_green2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_red2, _ = cv2.findContours(mask_red2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue2, _ = cv2.findContours(mask_blue2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Largest contour for red and green
    object_x_red = None
    object_x_green = None
    object_x_blue = None

    # x-coordinate for the red object frame
    if contours_red:
        largest_contour_red = max(contours_red, key=cv2.contourArea)
        if cv2.contourArea(largest_contour_red) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour_red)
            object_x_red = x + (w // 2)

    # x-coordinate for the red object frame2
    #if contours_red2:
       # largest_contour_red2 = max(contours_red2, key=cv2.contourArea)
       # if cv2.contourArea(largest_contour_red2) > 500:
         #   x, y, w, h = cv2.boundingRect(largest_contour_red2)
           # object_x_red = x + (w // 2)

    # x-coordinate for the green object frame
    if contours_green:
        largest_contour_green = max(contours_green, key=cv2.contourArea)
        if cv2.contourArea(largest_contour_green) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour_green)
            object_x_green = x + (w // 2)

    # x-coordinate for the green object frame2
    if contours_green2:
        largest_contour_green2 = max(contours_green2, key=cv2.contourArea)
        if cv2.contourArea(largest_contour_green2) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour_green2)
            object_x_green = x + (w // 2)

    # x-coordinate for the green object frame
    if contours_blue:
        largest_contour_blue = max(contours_blue, key=cv2.contourArea)
        if cv2.contourArea(largest_contour_blue) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour_blue)
            object_x_blue = x + (w // 2)

    # x-coordinate for the green object frame2
    if contours_blue2:
        largest_contour_blue2 = max(contours_blue2, key=cv2.contourArea)
        if cv2.contourArea(largest_contour_blue2) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour_blue2)
            object_x_blue = x + (w // 2)

    cv2.imshow("Frame", frame)
    cv2.imshow("Frame2", frame2)
    cv2.imshow("Mask Red", mask_red)
    cv2.imshow("Mask Green", mask_green)
    cv2.imshow("Mask Blue", mask_blue)
    cv2.imshow("Mask Red2", mask_red2)
    cv2.imshow("Mask Green2", mask_green2)
    cv2.imshow("Mask Blue2", mask_blue2)

    return object_x_red, object_x_green, object_x_blue

def release_camera():
    cam.release()
    cam2.release()
    cv2.destroyAllWindows()