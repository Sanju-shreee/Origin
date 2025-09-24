        # Step 3: Look for circular blobs (droplets) inside cropped frame
        droplet_blobs = loc.find_blobs(cropped_frame)
        droplets = [b for b in droplet_blobs if b["shape"] == "circle"]

        if not droplets:
            print("No droplet detected. Place a droplet on the surface.")
            annotated = cropped_frame.copy()
        else:
            annotated = cropped_frame.copy()
            for d in droplets:
                cx, cy = d["centroid"]
                print(f"Droplet detected: centroid={d['centroid']}, color={d['color']}, shape={d['shape']}")
                cv.circle(annotated, (cx, cy), 5, (0, 255, 0), -1)
                cv.drawContours(annotated, [d["contour"]], -1, (0, 0, 255), 2)
