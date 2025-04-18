#NEMA 17 STEPPPER MOTOR / DRIVER CONTROL
# Need to get RPiMotorLib to work soon:
# import rpimotorlib
# print("RPiMotorLib installed successfully!")

#Direction = 1 moves toward origin

from time import sleep
import RPi.GPIO as GPIO


# Define the GPIO Pins
DIR_pin = 20 # Direction pin
STEP_pin = 21 # sends pulses to move the motor

# Microstepping pins:
M0 = 14
M1 = 15
M2 = 18

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_pin, GPIO.OUT)
GPIO.setup(STEP_pin, GPIO.OUT)
GPIO.setup(M0, GPIO.OUT)
GPIO.setup(M1, GPIO.OUT)
GPIO.setup(M2, GPIO.OUT)

#Microstepping settings: (Change these to set to different modes):
# Options: "Full", "1/2", "1/4", "1/8", "1/16", "1/32"
Microstep_mode = "1/32"

# Reference that maps modes to M0, M1, and M2 settings:
Microstep_settings = {
    "Full" : (0, 0, 0),
    "1/2": (1, 0, 0),
    "1/4": (0, 1, 0),
    "1/8": (1, 1, 0),
    "1/16": (1, 1, 1),
    "1/32": (1, 0, 1)
}

#Apply chosen microstepping mode:
m0_state, m1_state, m2_state = Microstep_settings[Microstep_mode]
GPIO.output(M0, m0_state)
GPIO.output(M1, m1_state)
GPIO.output(M2, m2_state)

# Set direction (1 = CW, 0 = CCW)
#Direction = 1 moves toward origin
GPIO.output(DIR_pin, 0)

# Step delay (adjust for speed - slower for higher microstepping) 
# 200 steps = 1 full revolution in full step mode
STEPS = 3200
delay = 0.002 /16

# MOVE MOTOR
for x in range(STEPS):
    GPIO.output(STEP_pin, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP_pin, GPIO.LOW)
    sleep(delay)
   
GPIO.cleanup()

