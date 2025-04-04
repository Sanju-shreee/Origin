def find_frame_corners(image):
    # Convert image to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define colors (adjust as needed)
    lower_green = np.array([50, 100, 100])
    upper_green = np.array([70, 255, 255])

    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([130, 255, 255])

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
