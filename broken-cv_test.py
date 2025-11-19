#! /home/researchlab1/myvenv/bin/python3
import numpy as np
import cv2 as cv
import camera as loc
import csv
import os

# --- Initialize camera ---
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

# --- Step 4: Process droplets ---
droplet_data = []
count = 0

for blob in blobs:
    if blob["shape"] == "circle":  # only treat circular blobs as droplets
        count += 1
        cx, cy = blob["centroid"]
        color = blob["color"]

        cv.circle(cropped_frame, (cx, cy), 5, (0, 255, 0), -1)
        cv.drawContours(cropped_frame, [blob["contour"]], -1, (0, 255, 0), 2)
        droplet_data.append({
            "Number": count,
            "Color": color.capitalize(),
            "Coordinate": f"({cx}, {cy})"
        })

# --- Step 5: Display or warn ---
if not droplet_data:
    print("No droplets detected. Please place droplets on the surface.")
    cap.release()
    cv.destroyAllWindows()
    exit()

# --- Step 6: Print as a table ---
print("\nDetected Droplets:")
print(f"{'Number':<8} {'Color':<10} {'Coordinate'}")
print("-" * 35)
for d in droplet_data:
    print(f"{d['Number']:<8} {d['Color']:<10} {d['Coordinate']}")

# --- Step 7: Save as CSV ---
# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_dir = os.path.join(script_dir, "csv")
os.makedirs(csv_dir, exist_ok=True)

csv_path = os.path.join(csv_dir, "droplet_data.csv")

with open(csv_path, mode="w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["Number", "Color", "Coordinate"])
    writer.writeheader()
    writer.writerows(droplet_data)

print(f"\nDroplet data saved to: {csv_path}")

# --- Step 8: Show frame for visualization ---
cv.imshow("Cropped & Annotated", cropped_frame)
cv.waitKey(500)  # show for 0.5 sec
cv.destroyAllWindows()
cap.release()

# --- Step 9: Continue gantry workflow ---
print("\nProceeding to gantry homing and pickup sequence...")

