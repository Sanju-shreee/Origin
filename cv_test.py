#! /home/researchlab1/myvenv/bin/python3

# Activating the virtual environment
#venv_path = "/home/researchlab1/myvenv/bin/activate_this.py"
#with open(venv_path) as f:
 #   exec(f.read(), {'__file__': venv_path})

#print(f"Using python: {sys.executable}")
 
 
import numpy as np
import cv2 as cv
import camera as loc
from time import sleep
#centroid = []
cap = cv.VideoCapture(0)
while True:
    ret, frame = cap.read()
    cropped_frame = frame[128:380, 193:570]
    Centroid, annotated_image = loc.find_centroid(cropped_frame)
    cv.imshow('cropped frame', annotated_image)
    centroid = np.append(Centroid[0], Centroid[1])
    print(f'{Centroid[0], Centroid[1]}')
    #sleep(2)
    #if cv.waitKey(1) & 0xFF == ord('q'):
    break
cap.release()
cv.destroyAllWindows()
