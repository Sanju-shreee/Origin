#! /home/researchlab1/myvenv/bin/python3
import numpy as np
import cv2 as cv
import camera as loc

cap = cv.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- Step 1: Find all blobs in the frame ---
    blobs, annotated = loc.find_blobs(frame)

    # Separate markers (rectangles) and droplets (circles)
    markers = [b for b in blobs if b["shape"] == "rectangle"]
    droplets = [b for b in blobs if b["shape"] == "circle"]

    # If we have at least 2 markers, crop the frame
    if len(markers) >= 2:
        (x1, y1) = markers[0]["centroid"]
        (x2, y2) = markers[1]["centroid"]
        xmin, xmax = sorted([x1, x2])
        ymin, ymax = sorted([y1, y2])
        cropped_frame = frame[ymin:ymax, xmin:xmax]

        # Re-run detection on cropped frame
        droplets, annotated_crop = loc.find_blobs(cropped_frame)

        if not droplets:
            print("No droplet detected. Place a droplet on the surface.")
        else:
            for d in droplets:
                cx, cy = d["centroid"]
                print(f"Droplet detected: centroid={d['centroid']}, color={d['color']}, shape={d['shape']}")
                cv.circle(annotated_crop, (cx, cy), 5, (0, 255, 0), -1)
                cv.drawContours(annotated_crop, [d["contour"]], -1, (0, 255, 0), 2)

        cv.imshow("Cropped & Annotated", annotated_crop)

    else:
        print("Markers not detected. Place markers to crop frame.")
        cv.imshow("Frame", annotated)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
