import config


def steps_to_mm(steps):
    return steps/config.STEPS_MM

def mm_to_steps(mm):
    return round(mm*config.STEPS_MM)