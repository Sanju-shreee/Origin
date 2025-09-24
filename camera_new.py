import cv2
import numpy as np

def find_frame_corners(image):
    """
    Detect rectangular markers for cropping the frame.
    Returns two marker centroids and annotated frame.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Marker colors (adjust as needed)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([130, 255, 255])

    # Create masks
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Find contours
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

    if green_centroid:
        cv2.circle(image, green_centroid, 5, (0, 255, 0), -1)
    if blue_centroid:
        cv2.circle(image, blue_centroid, 5, (255, 0, 0), -1)

    return (green_centroid, blue_centroid), image


def find_centroid(image):
    """
    Detect circular droplet(s) and return centroid, annotated frame, and color.
    """
    annotated = image.copy()
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # HSV color ranges
    color_ranges = {
        'red': [(0, 150, 50), (10, 255, 150), (160, 150, 50), (179, 255, 150)],
        'green': [(35, 50, 50), (85, 255, 255)],
        'blue': [(90, 50, 50), (130, 255, 255)],
        'yellow': [(20, 100, 100), (30, 255, 255)]
    }

    droplets = []

    for color, ranges in color_ranges.items():
        if color == 'red':  # wrap-around HSV
            lower1 = np.array(ranges[0])
            upper1 = np.array(ranges[1])
            lower2 = np.array(ranges[2])
            upper2 = np.array(ranges[3])
            mask1 = cv2.inRange(hsv, lower1, upper1)
            mask2 = cv2.inRange(hsv, lower2, upper2)
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            lower = np.array(ranges[0])
            upper = np.array(ranges[1])
            mask = cv2.inRange(hsv, lower, upper)

        # Morphological cleanup
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 10:  # skip tiny noise
                continue

            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * (area / (perimeter ** 2))

            # Bounding rectangle for aspect ratio check (optional)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / h

            if circularity >= 0.7:  # roughly circular => droplet
                M = cv2.moments(cnt)
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                droplets.append({'centroid': (cx, cy), 'color': color, 'contour': cnt})
            else:
                # Rectangle-like blobs could be markers
                if 0.4 < aspect_ratio < 2.5:
                    cv2.rectangle(annotated, (x, y), (x + w, y + h), (255, 0, 0), 2)

    if droplets:
        # Choose largest droplet
        droplet = max(droplets, key=lambda d: cv2.contourArea(d['contour']))
        cx, cy = droplet['centroid']
        cv2.circle(annotated, (cx, cy), 3, (0, 255, 0), -1)
        cv2.drawContours(annotated, [droplet['contour']], -1, (0, 255, 0), 2)
        cv2.putText(annotated, droplet['color'], (cx + 5, cy - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return droplet['centroid'], annotated, droplet['color']

    return None, annotated, None


def find_error(x_desired, y_desired, centroid):
    cx, cy = centroid
    x_error = cx - x_desired
    y_error = cy - y_desired
    return x_error, y_error
