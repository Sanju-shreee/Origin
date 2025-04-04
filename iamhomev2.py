#HOMING
import stepper_x
import stepper_y
import stepper_z
import XYZ_Limits_Approach_Infinity
from time import sleep

microstepping_setting = "1/32"
stepfactor = 32
'''
if microstepping_setting == "1/32":
    stepfactor == 32
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
# HOMING SEQUENCE: Move towards limit switches until pressed
def home_axis(axis, stepper_module, steps=1, delay=0.5, direction=1):
    '''
    Moves the given axis towards its limit switch until it is pressed.
    :param axis: "X", "Y", or "Z"
    :param stepper_module: Corresponding stepper motor module (e.g., stepper_x)
    :param steps: Number of steps per iteration
    :param delay: Delay per step
    :param direction: Direction to move towards the limit switch
    '''
    print(f"Homing {axis}-axis...")
    while not XYZ_Limits_Approach_Infinity.is_limit_pressed(axis):
        print(f"{axis}-axis moving... Limit switch state: {XYZ_Limits_Approach_Infinity.is_limit_pressed(axis)}")
        stepper_module.move_motor(steps*stepfactor, direction, delay, microstepping_setting)
    
    print(f"{axis}-axis homed successfully!")

def homing_sequence():
    #Move Y and X to clear limit switches
    stepper_y.move_motor(40*stepfactor, 0, 0.002, microstepping_setting)
    stepper_z.move_motor(300*stepfactor, 0, 0.002, microstepping_setting)

    # Perform homing for each axis
    home_axis("X", stepper_x, 1, .5, 0)
    stepper_y.move_motor(40*stepfactor, 1, 0.002, microstepping_setting) #Undo Y Limit Switch Clearance
    home_axis("Y", stepper_y, 1, .5, 1)
    stepper_z.move_motor(300*stepfactor, 1, 0.002, microstepping_setting) #Undo X Limit Switch Clearance
    home_axis("Z", stepper_z, 10, .02, 1)
