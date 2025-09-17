#! /home/researchlab1/myvenv/bin/python3

import numpy as np
import cv2 as cv
import camera as loc
from time import sleep

cap = cv.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- Step 1: Find marker corners (circular blobs only) ---
    corners, marked_frame = loc.find_frame_corners(frame, circular_only=True, min_area=100, circ_thresh=0.7)
    if corners is None:
        print("Markers not detected.")
        cv.imshow("Frame", marked_frame)
        break
        continue

    (x1, y1), (x2, y2) = corners
    xmin, xmax = sorted([x1, x2])
    ymin, ymax = sorted([y1, y2])

    # --- Step 2: Crop the frame ---
    cropped_frame = frame[ymin:ymax, xmin:xmax]

    # --- Step 3: Find droplet centroid in cropped image (detect color + circularity) ---
    centroid, color, annotated = loc.find_centroid(
        cropped_frame,
        circular_only=True,
        min_area=50,
        circ_thresh=0.7,
        detect_color=True
    )

    if centroid:
        print(f"Droplet detected at {centroid}, color: {color}")
        cv.imshow("Cropped & Annotated", annotated)
    else:
        print("Droplet not detected.")
        cv.imshow("Cropped Frame", cropped_frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
