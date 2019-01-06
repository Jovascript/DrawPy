import threading
from collections import deque
import pigpio
from pigpio import OUTPUT
from drawpi.config import X_STEP, Y_STEP, X_DIR, Y_DIR, ENABLE_STEPPER
from drawpi.utils import chunks
from time import sleep

import logging
logger = logging.getLogger(__name__)

class XYSteppers(threading.Thread):
    '''Class for generating and executing pulses'''
    def __init__(self, pi: pigpio.pi):
        threading.Thread.__init__(self)
        # A daemon, cos
        self.daemon = True
        # A reference to the pigpio pi object
        self.pi = pi
        self.pi.wave_clear()

        # List of blocks, containing each set of pulses
        self.pulse_blocks = []

        # The Waveform IDs
        self.previous_wid = None
        self.current_wid = None

        # Threadsafe objects
        self.waveform_queue = deque()
        self.stop_event = threading.Event()
        self.done = threading.Event()
        # Start the thread
        self.start()

    def generate_waveforms(self, pulses):
        '''Generator, given a list of stepper pulses, return chunks of on and off pulses'''
        # Split into correctly sized chunks
        for chunk in chunks(pulses, round(MAX_PULSE_PER_WAVE/2)-1):
            wf = []
            # For each pulse
            for pulse in chunk:
                # Round delay, divide by 2(each pulse -> on and then off)
                delay = round(pulse[1]/2)
                # Pulse ON
                wf.append(pigpio.pulse(1 << pulse[0], 0, delay))
                # Pulse OFF
                wf.append(pigpio.pulse(0, 1 << pulse[0], delay))
            yield wf

    def add_pulses(self, pulses):
        pass

    def add_change_dir(self, dirX, dirY):
        pass



    def execute_pulses(self, pulses):
        '''Execute stepper pulses'''
        logger.debug("Executing {} Pulses".format(len(pulses)))
        for wf in self.generate_waveforms(pulses):
            # Queue to be executed by thread
            self.waveform_queue.append(wf)
        logger.debug("Done Executing Pulses")

    

    def run(self):
        '''Thread function'''
        # Running/runned waveforms
        while not self.stop_event.is_set():
            # If there are waveforms to execute
            if len(self.waveform_queue):
                # Clear the done event
                self.done.clear()
                # If space for adding a waveform
                if ((self.pi.wave_get_max_pulses() - self.pi.wave_get_pulses()) > MAX_PULSE_PER_WAVE) or ((self.pi.wave_get_max_cbs() - self.pi.wave_get_cbs()) > MAX_PULSE_PER_WAVE*2):
                    logger.debug("Sending New Waveform")
                    # Take a new waveform chunk
                    wf = self.waveform_queue.popleft()
                    # Add the chunk
                    self.pi.wave_add_generic(wf)
                    logger.debug("Loaded Pulses: {}".format(self.pi.wave_get_pulses()))

                    # Create the waveform in the DMC memory
                    self.current_wid = self.pi.wave_create()
                    # Send the wave
                    if self.previous_wid != None:
                        # If already transmitting, sync to previous
                        self.pi.wave_send_using_mode(self.current_wid,
                        pigpio.WAVE_MODE_ONE_SHOT_SYNC)
                    else:
                        # Just send
                        self.pi.wave_send_once(self.current_wid)
                    
                    # Wait for it to start being executed
                    while (self.pi.wave_tx_at() != self.current_wid):
                        pass
                    # We can now delete the previous waveform(if it exists)
                    if self.previous_wid != None:
                        self.pi.wave_delete(self.previous_wid)
                    self.previous_wid = self.current_wid
                # Debugging logs
                at = self.pi.wave_tx_at()
                msg = "Status: at:{}, current:{}, to go:{}".format(at, self.current_wid, len(self.waveform_queue))
                logger.debug(msg)
                logger.debug("CBS: {}".format(self.pi.wave_get_cbs()))
            else:
                at = self.pi.wave_tx_at()
                # If not busy
                if at == 9999:
                    # Tell everyone we are done
                    self.done.set()

    def slow_stop(self):
        # Remove pending waveforms
        self.waveform_queue.clear()

    def cancel(self):
        # Stop the whole thread
        self.stop_event.set()

