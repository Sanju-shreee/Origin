import cv2
import numpy as np

def find_frame_corners(image):
    # Convert image to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define colors (adjust as needed)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    
    #lower_pink = np.array([300 // 2, 50, 150])  # H: 300°/2 ≈ 150 HSV units
    #upper_pink = np.array([340 // 2, 180, 255])

    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([130, 255, 255])
    
    #lower_brown = np.array([10, 100, 20])    # Low brightness, reddish-orange hue
    #upper_brown = np.array([20, 255, 120])

    # Create masks
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Find contours for each
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours_green or not contours_blue:
        return None, image

    # Get centroids
    def get_centroid(cnt):
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            return None
        return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])

    green_centroid = get_centroid(max(contours_green, key=cv2.contourArea))
    blue_centroid = get_centroid(max(contours_blue, key=cv2.contourArea))

    # Optional: draw them for visualization
    if green_centroid and blue_centroid:
        cv2.circle(image, green_centroid, 5, (0, 255, 0), -1)
        cv2.circle(image, blue_centroid, 5, (255, 0, 0), -1)

    return (green_centroid, blue_centroid), image

# Original code starts here

def find_centroid(image):

    # Convert to HSV (Hue, Saturation, Value) color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define range for red color
    #Red wraps around in HSV, so we need two masks
    lower_red1 = np.array([0, 150, 50])
    upper_red1 = np.array([10, 255, 150])
    lower_red2 = np.array([160, 150, 50])
    upper_red2 = np.array([179, 255, 150])
    #Yellow
    #lower_yellow = np.array([20, 100, 100])
    #upper_yellow = np.array([30, 255, 255])
    #Blue
    #lower_blue = np.array([100, 100, 100])
    #upper_blue = np.array([130, 255, 255])


    # Create masks for red regions
    #mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    #mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, image

    # Find the largest contour (assuming it's the droplet)
    largest_contour = max(contours, key=cv2.contourArea)

    # Calculate centroid using moments
    M = cv2.moments(largest_contour)
    if M["m00"] == 0:
        return None, image

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    # Draw the centroid on the image (for visualization)
    cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)
    cv2.drawContours(image, [largest_contour], -1, (0, 255, 0), 2)

    return (cx, cy), image


# Function that determines and returns the x and y error
def find_error(x_desired, y_desired, centroid):
    cx = centroid[0]
    cy = centroid[1]
    x_error = cx - x_desired
    y_error = cy - y_desired
    return x_error, y_error

