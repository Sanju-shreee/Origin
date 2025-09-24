#! /home/researchlab1/myvenv/bin/python3
import numpy as np
import cv2 as cv
import camera as loc

cap = cv.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- Step 1: Find marker corners (green + blue rectangles) ---
    corners, marked_frame = loc.find_frame_corners(frame)
    if corners is None:
        print("Markers not detected.")
        cv.imshow("Frame", marked_frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    (x1, y1), (x2, y2) = corners
    xmin, xmax = sorted([x1, x2])
    ymin, ymax = sorted([y1, y2])

    # --- Step 2: Crop the frame using markers ---
    cropped_frame = frame[ymin:ymax, xmin:xmax]

    # --- Step 3: Detect circular blobs (droplets) ---
    blobs = loc.find_blobs(cropped_frame)
    droplets = [b for b in blobs if b["shape"] == "circle"]

    annotated = cropped_frame.copy()

    if not droplets:
        print("No droplet detected. Place a droplet on the surface.")
    else:
        for d in droplets:
            cx, cy = d["centroid"]
            color = d["color"]
            print(f"Droplet detected: centroid={d['centroid']}, color={color}, shape={d['shape']}")
            cv.circle(annotated, (cx, cy), 5, (0, 255, 0), -1)

            # Draw contour with matching color overlay
            color_map = {
                "red": (0, 0, 255),
                "green": (0, 255, 0),
                "blue": (255, 0, 0),
                "yellow": (0, 255, 255),
                "unknown": (255, 255, 255)
            }
            cv.drawContours(annotated, [d["contour"]], -1, color_map[color], 2)

    # --- Step 4: Show result ---
    cv.imshow("Cropped & Annotated", annotated)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
