import drawpi.config as config


def steps_to_mm(steps):
    return steps/config.STEPS_MM

def mm_to_steps(mm):
    return round(mm*config.STEPS_MM)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def frequency_to_delay(frequency):
    '''Convert x per second to us delay between pulses'''
    return round((1/frequency)*(10**6))