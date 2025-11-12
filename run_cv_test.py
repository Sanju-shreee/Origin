import subprocess
import sys
import os
import csv
import re

def detect_droplet():
    """
    Activates the virtual environment, runs the OpenCV test script, 
    and retrieves the detected centroid coordinates.

    :return: The centroid coordinates as a tuple (cx, cy) or None if not found.
    """

    venv_path = "/home/researchlab1/myvenv/bin/activate"
    command = f"source {venv_path} && python /home/researchlab1/Documents/Testing/cv_test.py"

    process = subprocess.run(command, shell=True, executable="/bin/bash", capture_output=True, text=True)

    print("STDOUT:", process.stdout)
    print("STDERR:", process.stderr)
    # File name
    csv_file = "/home/researchlab1/Documents/Testing/csv/droplet_data.csv"

    # Read CSV file
    droplets = {}

    with open(csv_file, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Extract coordinates safely using regex
            match = re.search(r"\((\d+),\s*(\d+)\)", row["Coordinate"])
            if match:
                cx, cy = int(match.group(1)), int(match.group(2))
                droplet_num = int(row["Number"])
                droplets[droplet_num] = {
                    "color": row["Color"],
                    "coords": (cx, cy)
                }
    if not droplets:
        print("No droplet data found in CSV file.")
        return None
    
    # ✅ At this point, you have a dictionary like:
    # {1: {'color': 'Red', 'coords': (154, 207)}, ...}

    # Let the user pick a droplet
    print("Available droplets:")
    for num, info in droplets.items():
        print(f"{num}. {info['color']} at {info['coords']}")

    while True:
        try:
            selected_num = int(input("\nEnter the droplet number to use: "))
            if selected_num in droplets:
                drop_px = droplets[selected_num]["coords"]
                print(f"\nSelected droplet #{selected_num} ({droplets[selected_num]['color']})")
                print(f"({cx}, {cy})")
                break
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Please enter a valid integer.")

def run_cv_test():
    """
    Runs droplet detection once and returns the droplet's centroid coordinates.
    Returns None if no droplet is detected.
    """
    print("Running droplet detection...")
    drop_px = detect_droplet()

    if drop_px:
        print(f"Droplet detected at pixel coordinates: {drop_px}")
        return drop_px
    else:
        print("No droplet detected.")
        return None

