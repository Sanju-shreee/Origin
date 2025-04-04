import numpy as np
import cv2 as cv
import camera as loc
from time import sleep

cap = cv.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- Step 1: Find marker corners ---
    corners, marked_frame = loc.find_frame_corners(frame)
    if corners is None:
        print("Markers not detected.")
        cv.imshow("Frame", marked_frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    (x1, y1), (x2, y2) = corners
    # Ensure correct rectangle coordinates
    xmin, xmax = sorted([x1, x2])
    ymin, ymax = sorted([y1, y2])

    # --- Step 2: Crop the frame ---
    cropped_frame = frame[ymin:ymax, xmin:xmax]

    # --- Step 3: Find droplet centroid in cropped image ---
    centroid, annotated = loc.find_centroid(cropped_frame)
    if centroid:
        cv.imshow("Cropped & Annotated", annotated)
        print(f"Droplet pixel coords: {centroid}")
    else:
        print("Droplet not detected.")
        cv.imshow("Cropped Frame", cropped_frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
