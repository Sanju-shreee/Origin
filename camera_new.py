import cv2
import numpy as np

def detect_color(hsv_value):
    """Classify HSV value into a basic color name."""
    h, s, v = hsv_value

    if s < 40 and v > 200:
        return "white"
    if v < 50:
        return "black"
    if h < 10 or h > 170:
        return "red"
    if 10 <= h < 30:
        return "orange/yellow"
    if 30 <= h < 90:
        return "green"
    if 90 <= h < 130:
        return "blue"
    if 130 <= h < 170:
        return "purple"
    return "unknown"

def classify_shape(contour):
    """Determine if a contour is rectangular or circular."""
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

    if len(approx) == 4:
        return "rectangle"
    else:
        return "circle"

def get_centroid(contour):
    """Return centroid of a contour."""
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])

def find_blobs(image):
    """Detect blobs and classify them by shape + color."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    blobs = []
    for cnt in contours:
        if cv2.contourArea(cnt) < 50:  # skip very small noise
            continue

        shape = classify_shape(cnt)
        centroid = get_centroid(cnt)

        if centroid is None:
            continue

        # Get average color inside contour
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        mean_val = cv2.mean(hsv, mask=mask)
        color = detect_color(mean_val[:3])

        blobs.append({
            "shape": shape,
            "centroid": centroid,
            "color": color,
            "contour": cnt
        })

    return blobs, image
