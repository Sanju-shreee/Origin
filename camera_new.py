import cv2
import numpy as np

# ---------------- HSV Color Ranges ----------------
COLOR_RANGES = {
    "red":    [(np.array([0, 120, 70]),   np.array([10, 255, 255])),
               (np.array([160, 120, 70]), np.array([179, 255, 255]))],  # red wraps around
    "green":  [(np.array([35, 50, 50]),   np.array([85, 255, 255]))],
    "blue":   [(np.array([90, 50, 50]),   np.array([130, 255, 255]))],
    "yellow": [(np.array([20, 100, 100]), np.array([35, 255, 255]))]
}


# ---------------- Marker detection (green + blue rectangles) ----------------
def find_frame_corners(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Combine masks for green + blue
    mask = None
    for color in ["green", "blue"]:
        for (lower, upper) in COLOR_RANGES[color]:
            c_mask = cv2.inRange(hsv, lower, upper)
            mask = c_mask if mask is None else cv2.bitwise_or(mask, c_mask)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, image

    def get_centroid(cnt):
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            return None
        return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])

    corners = []
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4 and cv2.contourArea(cnt) > 200:  # rectangle marker
            c = get_centroid(cnt)
            if c:
                corners.append(c)
                cv2.circle(image, c, 5, (255, 255, 255), -1)

    return (corners if len(corners) >= 2 else None), image


# ---------------- Helper: Determine color inside ROI ----------------
def classify_color_from_mask(hsv_roi):
    """Classify color based on HSV pixel ratios inside ROI."""
    total_pixels = hsv_roi.shape[0] * hsv_roi.shape[1]
    for color, ranges in COLOR_RANGES.items():
        mask_total = None
        for (lower, upper) in ranges:
            mask = cv2.inRange(hsv_roi, lower, upper)
            mask_total = mask if mask_total is None else cv2.bitwise_or(mask_total, mask)
        ratio = cv2.countNonZero(mask_total) / float(total_pixels)
        if ratio > 0.3:  # at least 30% of ROI matches
            return color
    return "unknown"


# ---------------- Main: Detect all circular droplets ----------------
def find_blobs(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Combine all color masks
    mask_total = None
    for ranges in COLOR_RANGES.values():
        for (lower, upper) in ranges:
            mask = cv2.inRange(hsv, lower, upper)
            mask_total = mask if mask_total is None else cv2.bitwise_or(mask_total, mask)

    contours, _ = cv2.findContours(mask_total, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []

    frame_area = image.shape[0] * image.shape[1]
    annotated_frame = image.copy()

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 50 or area > 0.4 * frame_area:
            continue

        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue

        circularity = (4 * np.pi * area) / (perimeter * perimeter)
        shape = "circle" if circularity > 0.8 else "rectangle"

        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        x, y, w, h = cv2.boundingRect(cnt)
        roi_hsv = hsv[y:y+h, x:x+w]
        color = classify_color_from_mask(roi_hsv)

        blobs.append({
            "contour": cnt,
            "centroid_x": cx,
            "centroid_y": cy,
            "shape": shape,
            "color": color
        })

        # Draw blob outline + centroid
        cv2.drawContours(annotated_frame, [cnt], -1, (0, 255, 0), 2)
        cv2.circle(annotated_frame, (cx, cy), 4, (0, 255, 0), -1)
        cv2.putText(annotated_frame, f"{color}", (cx + 10, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # ---- Overlay a mini data table on the top left ----
    if blobs:
        overlay = annotated_frame.copy()
        cv2.rectangle(overlay, (10, 10), (260, 40 + 20 * len(blobs)), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, annotated_frame, 0.5, 0, annotated_frame)
        cv2.putText(annotated_frame, "Droplet Summary", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y_offset = 55
        for i, blob in enumerate(blobs, start=1):
            text = f"{i}. {blob['color']} ({blob['centroid_x']},{blob['centroid_y']})"
            cv2.putText(annotated_frame, text, (25, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 255, 200), 1)
            y_offset += 20

    return blobs, annotated_frame
