import cv2
import numpy as np

def initializate_cameras(num_players):
    cam = cv2.VideoCapture(0)
    cam2 = cv2.VideoCapture(1) if num_players == 2 else None
    if not cam.isOpened() or (num_players == 2 and not cam2.isOpened()):
        print("Erro ao iniciar as câmaras.")
        exit()
    return cam, cam2

# Color range for segmentation
color_ranges = {
    "green": (np.array([35, 100, 100]), np.array([85, 255, 255])),
    "blue": (np.array([100, 150, 50]), np.array([140, 255, 255]))
}

# Function to process the webcam input and show segmentation result
def process_frame(cam, cam2=None):
    ret, frame = cam.read()
    ret2, frame2 = (None, None)
    if cam2:
        ret2, frame2 = cam2.read()

    if not ret or (cam2 and not ret2):
        return None, None, None

    frame = cv2.flip(frame, 1)  # Flip the frame horizontally
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Convert to HSV color space

    # Create masks for green and blue colors in the frame
    mask_green = cv2.inRange(hsv_frame, *color_ranges["green"])

    # Segmentation results for the frame
    segmentation_green = cv2.bitwise_and(frame, frame, mask=mask_green)

    # Display results for the frame
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask Green", mask_green)
    cv2.imshow("Segmentation Green", segmentation_green)

    if cam2:
        # Process the second camera frame only if in two-player mode
        hsv_frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)  # Convert second frame to HSV

        # Create masks for green and blue colors in frame2
        mask_green2 = cv2.inRange(hsv_frame2, *color_ranges["green"])
        mask_blue2 = cv2.inRange(hsv_frame2, *color_ranges["blue"])
        mask_blue = cv2.inRange(hsv_frame, *color_ranges["blue"])

        # Segmentation results for the second frame
        segmentation_blue = cv2.bitwise_and(frame, frame, mask=mask_blue)
        segmentation_green2 = cv2.bitwise_and(frame2, frame2, mask=mask_green2)
        segmentation_blue2 = cv2.bitwise_and(frame2, frame2, mask=mask_blue2)

        # Display results for the second frame
        cv2.imshow("Frame2", frame2)
        cv2.imshow("Mask Green2", mask_green2)
        cv2.imshow("Segmentation Green2", segmentation_green2)

        # Show blue masks only in two-player mode
        cv2.imshow("Mask Blue2", mask_blue2)
        cv2.imshow("Segmentation Blue2", segmentation_blue2)

        cv2.imshow("Mask Blue", mask_blue)
        cv2.imshow("Segmentation Blue", segmentation_blue)

    # Contours for the frame
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if cam2:
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    object_x_green = None
    object_x_blue = None

    # x-coordinate for the green object in frame
    if contours_green:
        largest_contour_green = max(contours_green, key=cv2.contourArea)
        if cv2.contourArea(largest_contour_green) > 500:
            x, y, w, h = cv2.boundingRect(largest_contour_green)
            object_x_green = x + (w // 2)

    # x-coordinate for the blue object in frame
    if cam2:
        if contours_blue:
            largest_contour_blue = max(contours_blue, key=cv2.contourArea)
            if cv2.contourArea(largest_contour_blue) > 500:
                x, y, w, h = cv2.boundingRect(largest_contour_blue)
                object_x_blue = x + (w // 2)

    if cam2:
        return object_x_green, object_x_blue  # Return coordinates for both players
    else:
        return object_x_green  # Return only for the single player

def release_camera(cam, cam2=None):
    cam.release()
    if cam2:
        cam2.release()
    cv2.destroyAllWindows()
