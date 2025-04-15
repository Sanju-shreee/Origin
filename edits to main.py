
# moving claw out of the way of the camera
iamhome.home_axis("X", stepper_x, 1, 0.0002/16, 0)
print("Homing x to clear for camera vision")

drop_px_check = run_cv_test.run_cv_test()

if drop_px_check:
    print("Droplet detected on surface. Retrying pickup.")
    # Moving the Y axis to droplet's initial y position
    stepper_y.move_motor(y_steps*stepfactor, 0, 0.0002/16, microstepping_setting)
    # Moving the X axis to droplet's initial x position
    stepper_x.move_motor(x_steps*stepfactor, 1, 0.0002/16, microstepping_setting)
    # open claw
    claw.open_claw(step_delay)
    sleep(1)
    # z axis down
    stepper_z.move_motor(300*stepfactor, 0, 0.00002/16, microstepping_setting)
    # close claw
    claw.close_claw(step_delay)
    # Z-axis moves up for clearance
    stepper_z.move_motor(300*stepfactor, 1, 0.00002/16, microstepping_setting)
    
else:
    ("Droplet in claw. Continuing sequence.")
