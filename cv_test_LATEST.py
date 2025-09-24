import cv2
import camera as loc

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- Step 1: Find marker corners ---
    corners, marked_frame = loc.find_frame_corners(frame)
    if corners is None:
        print("Markers not detected.")
        cv2.imshow("Frame", marked_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    (x1, y1), (x2, y2) = corners
    xmin, xmax = sorted([x1, x2])
    ymin, ymax = sorted([y1, y2])

    # --- Step 2: Crop frame ---
    cropped_frame = frame[ymin:ymax, xmin:xmax]

    # --- Step 3: Find droplet centroid in cropped frame ---
    centroid, annotated, color = loc.find_centroid(cropped_frame)
    if centroid:
        print(f"Droplet detected at {centroid}, color: {color}")
        cv2.imshow("Cropped & Annotated", annotated)
    else:
        print("Droplet not detected.")
        cv2.imshow("Cropped Frame", cropped_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
