# MAIN SCRIPT FOR ROBOTIC GANTRY

import numpy as np
import run_cv_test
import stepper_x
import stepper_y
import stepper_z
import XYZ_Limits_Approach_Infinity
import claw
from claw import open_claw, close_claw, cleanup
from time import sleep
import iamhome

microstepping_setting = "1/32"
stepfactor = 32
'''
if microstepping_setting == "1/32":
    stepfactor = 32
elif microstepping_setting == "1/16":
    stepfactor == 16
elif microstepping_setting == "1/8":
    stepfactor == 8
elif microstepping_setting == "1/4":
    stepfactor == 4
elif microstepping_setting == "1/2":
    stepfactor == 2
else:
    stepfactor == 1
'''
#Prompt user to place droplet on surface. Loop until the user presses ENTER without typing anything
while True:
    user_input = input("Please press ENTER after you successfully place a droplet on the surface (within frame)!")

    # Check if the input is empty (i.e., they pressed enter without typing anything)
    if user_input == "":
        print("Proceeding to the next step...")
        break  # Exit the loop and continue with the next step
    else:
        print("Invalid input. Please press ENTER without typing anything.")

# Creating a function to ensure user enters a valid integer as fluid droplet's end coordinates

def get_integers(prompt):
    while True: #keeps asking until the user enters a valid integer
        try:
            return int(input(prompt))
        except ValueError:
            print("YIKES! Error: Please enter a valid integer.")

Max_X_steps = 15400
Max_Y_steps = 16000
conv_mmtosteps = 4.7619

# End Coordinates the droplet must be transported to in units of mm            
while True:
    EndPointX = get_integers('Enter desired X coordinate between 0-100 (mm): ')
    EndPoint_Xsteps = int(EndPointX*conv_mmtosteps*32)
    if 0 <= EndPoint_Xsteps <= Max_X_steps:
        break
    else:
        print(f"Please enter a value between 0 and {int(Max_X_steps/(32*conv_mmtosteps))}.")
        
while True:
    EndPointY = get_integers('Enter desired Y coordinate between 0-105 (mm): ')
    EndPoint_Ysteps = int(EndPointY*conv_mmtosteps*32)
    if 0 <= EndPoint_Ysteps <= Max_Y_steps:
        break
    else:
        print(f"Please enter a value between 0 and {int(Max_Y_steps/(32*conv_mmtosteps))}.")

EndPoint = np.array([EndPointX, EndPointY])
# Prints end coordinates
print(EndPoint)

# Run the homing sequence (Gantry goes to (0,0,0) defined by limit switches)
iamhome.homing_sequence()

# Run the CV test and get the centroid
drop_px = run_cv_test.run_cv_test()

# Now drop_px contains the centroid coordinates (cx, cy)
if drop_px:
    print(f"Centroid's pixels: {drop_px}")
    print(f"Calculating droplet's coordinates...")
    conv_pxtocoord = 2.12658
    # distance from camera's origin to droplet's centroid in terms of mm
    drop_coord = np.array(drop_px)/conv_pxtocoord
    print(f"Drop Coordinate: {drop_coord}")
else:
    print("No centroid found. Please ensure droplet of 30 microliters is in frame and try again!")

# Please note: 3.13 is the y offset distance from the Limit switch Gantry origin to the Camera's origin
# Distance from droplet's origin to the Gantry's origin (Limit switches) in mm
drop_origin = (3.13 + drop_coord[0],177.4 - drop_coord[1]) #(y,x)
claw_origin = (30.8, 49.8) #(y,x)

# Distance from droplet's origin to the claw origin in units of mm?
claw_drop = (drop_origin[0] - claw_origin[0], drop_origin[1] - claw_origin[1])

# Distance from droplet's origin to the claw in terms of steps
x_steps = int(claw_drop[1]*conv_mmtosteps)
y_steps = int(claw_drop[0]*conv_mmtosteps)

# Moving the Y axis to droplet's initial y position
stepper_y.move_motor(y_steps*stepfactor, 0, 0.0002/16, microstepping_setting)

# Moving the X axis to droplet's initial x position
stepper_x.move_motor(x_steps*stepfactor, 1, 0.0002/16, microstepping_setting)

# Open Claw: Servo motor rotates (to 85 degrees)
# Specifiy step delay for the servo motor to adjust speed of claw
step_delay = 0.05
claw.open_claw(step_delay)

sleep(1)

# Z axis moves down to surface.
# The droplet should be in between the left and right claws after the Z axis has come down. If not, camera calibration (mechanical) might be off.
stepper_z.move_motor(915*stepfactor, 0, 0.00002/16, microstepping_setting)

sleep(1)

#Closing Claw: Servo motor rotates (to 68 degrees)
claw.close_claw(step_delay)

sleep(3)

# Z-axis moves up for clearance
stepper_z.move_motor(300*stepfactor, 1, 0.00002/16, microstepping_setting)

# Convert the droplet's end coordinates from mm to steps
EndPoint_Xsteps = int(EndPointX*conv_mmtosteps)
EndPoint_Ysteps = int(EndPointY*conv_mmtosteps)

# Calculate distance (in steps) to move x & y axes
X_final = x_steps - EndPoint_Xsteps
Y_final = y_steps - EndPoint_Ysteps

# Conditional Movement: X
if X_final > 0:
    stepper_x.move_motor(X_final*stepfactor, 0, 0.0002/16, microstepping_setting)
    print("X moving in -x direction")
else:
    X_final = abs(X_final)
    stepper_x.move_motor(X_final*stepfactor, 1, 0.0002/16, microstepping_setting)
    print("X moving in +x direction")

# Conditional Movement: Y
if Y_final > 0:
    stepper_y.move_motor(Y_final*stepfactor, 1, 0.0002/16, microstepping_setting)
    print("X moving in -y direction")
else:
    Y_final = abs(Y_final)
    stepper_y.move_motor(Y_final*stepfactor, 0, 0.0002/16, microstepping_setting)
    print("X moving in +y direction")

# Z-axis moves down
stepper_z.move_motor(300*stepfactor, 0, 0.00002/16, microstepping_setting)

# Claw opens
#claw.servo_angle(85)
claw.open_claw(step_delay)
print("Droplet has been placed!")

sleep(2)

# Z up
stepper_z.move_motor(615*stepfactor, 1, 0.00002/16, microstepping_setting)

# close claw
#claw.servo_angle(68)
claw.close_claw(step_delay)

# Home
if EndPoint_Ysteps*stepfactor > 40*stepfactor:
    print("Not moving to clear Y Limit Switch")
    iamhome.home_axis("X", stepper_x, 1, 0.0002/16, 0) #homing x
    iamhome.home_axis("Y", stepper_y, 1, 0.0002/16, 1) #homing y
    iamhome.home_axis("Z", stepper_z, 1, 0.00002/16, 1) #homing z
else:
    print("Moving to clear Y Limit Switch")
    iamhome.homing_sequence()

# Cleanup GPIO
XYZ_Limits_Approach_Infinity.cleanup()
stepper_x.cleanup()
stepper_y.cleanup()
stepper_z.cleanup()
claw.cleanup()

    
