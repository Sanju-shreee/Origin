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

# Prompt user to place droplet on surface. Loop until the user presses ENTER without typing anything
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

# End Coordinates the droplet must be transported to in units of mm            
EndPointX = get_integers('Enter desired X coordinate (mm): ')
EndPointY = get_integers('Enter desired Y coordinate (mm): ')
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

conv_mmtosteps = 4.7619

# Distance from droplet's origin to the claw in terms of steps
x_steps = int(claw_drop[1]*conv_mmtosteps)
y_steps = int(claw_drop[0]*conv_mmtosteps)

# Moving the Y axis to droplet's initial y position
stepper_y.move_motor(y_steps, 0, 0.002, "Full")

# Moving the X axis to droplet's initial x position
stepper_x.move_motor(x_steps, 1, 0.002, "Full")

# Open Claw: Servo motor rotates (to 85 degrees)
# Specifiy step delay for the servo motor to adjust speed of claw
step_delay = 0.05
claw.open_claw(step_delay)

sleep(1)

# Z axis moves down to surface.
# The droplet should be in between the left and right claws after the Z axis has come down. If not, camera calibration (mechanical) might be off.
stepper_z.move_motor(940, 0, 0.002, "Full")

sleep(1)

#Closing Claw: Servo motor rotates (to 68 degrees)
claw.close_claw(step_delay)

sleep(3)

# Z-axis moves up for clearance
stepper_z.move_motor(300, 1, 0.002, "Full")

# Convert the droplet's end coordinates from mm to steps
EndPoint_Xsteps = int(EndPointX*conv_mmtosteps)
EndPoint_Ysteps = int(EndPointY*conv_mmtosteps)

# Calculate distance (in steps) to move x & y axes
X_final = x_steps - EndPoint_Xsteps
Y_final = y_steps - EndPoint_Ysteps

# Conditional Movement: X
if X_final > 0:
    stepper_x.move_motor(X_final, 0, 0.002, "Full")
    print("X moving in -x direction")
else:
    stepper_x.move_motor(X_final, 1, 0.002, "Full")
    print("X moving in +x direction")

# Conditional Movement: Y
if Y_final > 0:
    stepper_y.move_motor(Y_final, 1, 0.002, "Full")
    print("X moving in -y direction")
else:
    stepper_y.move_motor(Y_final, 0, 0.002, "Full")
    print("X moving in +y direction")

# Z-axis moves down
stepper_z.move_motor(300, 0, 0.002, "Full")

# Claw opens
#claw.servo_angle(85)
claw.open_claw(step_delay)
print("Droplet has been placed!")

sleep(2)

# Z up
stepper_z.move_motor(640, 1, 0.002, "Full")

# close claw
#claw.servo_angle(68)
claw.close_claw(step_delay)

sleep(2)

# Home
#taking X home
stepper_y.move_motor(40, 0, 0.002, "Full")# Y Limit Switch Clearance
stepper_x.move_motor(EndPoint_Xsteps, 0, 0.002, "Full")
iamhome.home_axis("X", stepper_x, 1, .5, 0)
#taking Y home
stepper_y.move_motor(40, 1, 0.002, "Full")# Undo Y Limit Switch Clearance
stepper_y.move_motor(EndPoint_Ysteps, 1, 0.002, "Full")
iamhome.home_axis("Y", stepper_y, 1, .5, 0)
#taking Z home
iamhome.home_axis("Z", stepper_z, 10, .02, 1)


# Cleanup GPIO
XYZ_Limits_Approach_Infinity.cleanup()
stepper_x.cleanup()
stepper_y.cleanup()
stepper_z.cleanup()
claw.cleanup()
