#! /home/researchlab1/myvenv/bin/python3
import cv2 as cv
import camera as loc

cap = cv.VideoCapture(0)

detected_once = False  # flag so we only detect one droplet

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
    xmin, xmax = sorted([x1, x2])
    ymin, ymax = sorted([y1, y2])

    # --- Step 2: Crop the frame ---
    cropped_frame = frame[ymin:ymax, xmin:xmax]

    # --- Step 3: Detect circular blobs (droplets) ---
    blobs = loc.find_blobs(cropped_frame)
    droplets = [b for b in blobs if b["shape"] == "circle"]

    annotated = cropped_frame.copy()

    if not detected_once:
        if not droplets:
            print("No droplet detected. Place a droplet on the surface.")
        else:
            for d in droplets:
                cx, cy = d["centroid"]
                color = d["color"]
                print(f"Droplet detected: centroid={d['centroid']}, color={color}, shape={d['shape']}")
                cv.circle(annotated, (cx, cy), 5, (0, 255, 0), -1)
                cv.drawContours(annotated, [d["contour"]], -1, (0, 255, 0), 2)
            detected_once = True  # ✅ stop after first detection

    # --- Step 4: Show result ---
    cv.imshow("Cropped & Annotated", annotated)

    # If we've already detected, wait for user to quit
    if detected_once:
        if cv.waitKey(0) & 0xFF == ord('q'):
            break
    else:
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv.destroyAllWindows()
