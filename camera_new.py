import cv2
import numpy as np

# ---------------- Marker detection (green + blue rectangles) ----------------
def find_frame_corners(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define marker colors
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([130, 255, 255])

    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours_green or not contours_blue:
        return None, image

    def get_centroid(cnt):
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            return None
        return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])

    green_centroid = get_centroid(max(contours_green, key=cv2.contourArea))
    blue_centroid = get_centroid(max(contours_blue, key=cv2.contourArea))

    if green_centroid and blue_centroid:
        cv2.circle(image, green_centroid, 5, (0, 255, 0), -1)
        cv2.circle(image, blue_centroid, 5, (255, 0, 0), -1)

    return (green_centroid, blue_centroid), image


# ---------------- General blob detection (droplets etc.) ----------------
def classify_color(hsv_val):
    h, s, v = hsv_val
    if 0 <= h <= 10 or 160 <= h <= 179:
        return "red"
    elif 20 <= h <= 35:
        return "yellow"
    elif 35 < h <= 85:
        return "green"
    elif 100 <= h <= 130:
        return "blue"
    else:
        return "unknown"

def find_blobs(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 50:  # ignore tiny noise
            continue

        # Shape check: circular vs rectangular
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)

        shape = "circle"
        if len(approx) == 4:
            shape = "rectangle"

        # Centroid
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Color detection at centroid
        hsv_val = hsv[cy, cx]
        color = classify_color(hsv_val)

        blobs.append({
            "contour": cnt,
            "centroid": (cx, cy),
            "shape": shape,
            "color": color
        })

    return blobs
