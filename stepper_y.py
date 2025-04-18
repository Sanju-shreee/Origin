#NEMA 17 STEPPPER MOTOR / DRIVER CONTROL
# Need to get RPiMotorLib to work soon:
# import rpimotorlib
# print("RPiMotorLib installed successfully!")

#Direction = 1 moves toward origin

from time import sleep
import RPi.GPIO as GPIO


microstepping_setting = "1/32"
stepfactor = 32

# Define the GPIO Pins
DIR_pin = 20 # Direction pin
STEP_pin = 21 # sends pulses to move the motor

# Microstepping pins:
M0 = 14
M1 = 15
M2 = 18

# Setup GPIO mode
#GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_pin, GPIO.OUT)
GPIO.setup(STEP_pin, GPIO.OUT)
GPIO.setup(M0, GPIO.OUT)
GPIO.setup(M1, GPIO.OUT)
GPIO.setup(M2, GPIO.OUT)

#Microstepping settings: (Change these to set to different modes):
# Options: "Full", "1/2", "1/4", "1/8", "1/16", "1/32"
Microstep_mode = microstepping_setting

# Reference that maps modes to M0, M1, and M2 settings:
Microstep_settings = {
    "Full" : (0, 0, 0),
    "1/2": (1, 0, 0),
    "1/4": (0, 1, 0),
    "1/8": (1, 1, 0),
    "1/16": (1, 1, 1),
    "1/32": (1, 0, 1)
}

def move_motor(steps, direction, delay, microstep_mode):
    """
    Function to move the stepper motor
    
    """
    
    if microstep_mode not in Microstep_settings:
        raise ValueError("YIKES! Invalid microstepping mode! Choose from: " + ", ".join(Microstep_settings.keys()))
    
    #Apply chosen microstepping mode:
    m0_state, m1_state, m2_state = Microstep_settings[Microstep_mode]
    GPIO.output(M0, int(m0_state))
    GPIO.output(M1, int(m1_state))
    GPIO.output(M2, int(m2_state))

    # Set direction (1 = CW, 0 = CCW)
    GPIO.output(DIR_pin, direction)

    # MOVE MOTOR
    for x in range(steps):
        GPIO.output(STEP_pin, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP_pin, GPIO.LOW)
        sleep(delay)

def cleanup():
        GPIO.cleanup()

