#! /home/researchlab1/myvenv/bin/python3
import numpy as np
import cv2 as cv
import camera as loc

cap = cv.VideoCapture(0)

ret, frame = cap.read()
if not ret:
    print("Camera not available.")
    cap.release()
    cv.destroyAllWindows()
    exit()

# --- Step 1: Find marker corners ---
corners, marked_frame = loc.find_frame_corners(frame)
if corners is None or len(corners) < 2:
    print("Markers not detected.")
    cap.release()
    cv.destroyAllWindows()
    exit()

(x1, y1), (x2, y2) = corners
xmin, xmax = sorted([x1, x2])
ymin, ymax = sorted([y1, y2])

# --- Step 2: Crop the frame ---
cropped_frame = frame[ymin:ymax, xmin:xmax]

# --- Step 3: Find blobs inside cropped image ---
blobs = loc.find_blobs(cropped_frame)

found_droplet = False
for blob in blobs:
    if blob["shape"] == "circle":  # only treat circular blobs as droplets
        found_droplet = True
        cx, cy = blob["centroid"]
        color = blob["color"]

        cv.circle(cropped_frame, (cx, cy), 5, (0, 255, 0), -1)
        cv.drawContours(cropped_frame, [blob["contour"]], -1, (0, 255, 0), 2)

        #print(f"Droplet detected → Centroid: {cx, cy}, Color: {color}")
        print(f"{cx, cy}")

""""if not found_droplet:
    print("No droplet detected. Please place a droplet on the surface.")
    cap.release()
    cv.destroyAllWindows()
    exit()
"""
# Show final annotated snapshot (optional, for debugging)
cv.imshow("Cropped & Annotated", cropped_frame)
cv.waitKey(500)  # show for 0.5 sec, then continue automatically
cv.destroyAllWindows()

cap.release()

# ---------------- Continue to gantry workflow ----------------
# At this point, pass (cx, cy) to your homing + claw pickup functions
#print("Proceeding to gantry homing and pickup sequence...")
