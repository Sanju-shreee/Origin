import pigpio
from time import sleep

SERVO_PIN = 17  # Using GPIO Pin 17 for servo control
OPEN_ANGLE = 85
CLOSED_ANGLE = 68

# Initialize pigpio
pi = pigpio.pi()

if not pi.connected:
    print("Couldn't connect to pigpio daemon. Make sure it's running.")
    exit()

# Function to set the servo angle
def servo_angle(angle):
    if 0 <= angle <= 180:
        pulse_width = (500 + (angle * 2000 // 180))  # Convert angle to pulse width
        pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
        print(f"Moving servo to {angle} degrees (Pulse Width: {pulse_width} µs)")
    else:
        print("Please enter a valid angle between 0 and 180.")

# Function to move the servo smoothly from one angle to another
def move_servo_smoothly(start_angle, end_angle, step_delay, step_size=2):
    """
    Gradually moves the servo from start_angle to end_angle in small steps.
    - step_delay: Delay between each step to control speed.
    - step_size: Angle increment per step (lower value = smoother motion).
    """
    step = step_size if start_angle < end_angle else -step_size
    for angle in range(start_angle, end_angle + step, step):
        servo_angle(angle)
        sleep(step_delay)  # Small delay for smooth motion
        
    # Stop the servo signal once movement is done - do not use this 
    # pi.set_servo_pulsewidth(SERVO_PIN, 0)

# Function to open the claw gradually
def open_claw(step_delay):
    print("Opening Claw...")
    move_servo_smoothly(CLOSED_ANGLE, OPEN_ANGLE, step_delay)

# Function to close the claw gradually
def close_claw(step_delay):
    print("Closing Claw...")
    move_servo_smoothly(OPEN_ANGLE, CLOSED_ANGLE, step_delay)

# Cleanup function to stop the servo when done
def cleanup():
    print("Cleaning up...")
    pi.set_servo_pulsewidth(SERVO_PIN, 0)  # Stop sending pulses
    pi.stop()  # Clean up the pigpio library
