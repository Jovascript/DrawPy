import threading
from collections import deque
import pigpio
from pigpio import OUTPUT
from drawpi.config import X_STEP, Y_STEP, X_DIR, Y_DIR, ENABLE_STEPPER, MAX_PULSE_PER_WAVE
from drawpi.utils import chunks
import logging
logging.getLogger(__name__)
class XYSteppers(threading.Thread):
    def __init__(self, pi: pigpio.pi):
        threading.Thread.__init__(self)
        self.daemon = True
        self.pi = pi
        self.pi.wave_clear()

        self.pulse_blocks = []

        self.previous_wid = None
        self.current_wid = None

        self.waveform_queue = deque()
        self.stop_event = threading.Event()
        self.done = threading.Event()
        self.start()

    def generate_waveforms(self, pulses):
        for chunk in chunks(pulses, round(MAX_PULSE_PER_WAVE/2)-1):
            wf = []
            for pulse in chunk:
                delay = round(pulse[1]/2)
                # Pulse ON
                wf.append(pigpio.pulse(1 << pulse[0], 0, delay))
                # Pulse OFF
                wf.append(pigpio.pulse(0, 1 << pulse[0], delay))
            yield wf

    def execute_pulses(self, pulses):
        logger.debug("Executing {} Pulses".format(len(pulses)))
        for wf in self.generate_waveforms(pulses):
            self.waveform_queue.append(wf)
        logger.debug("Done Executing Pulses")

    def run(self):
        running_wids = deque()
        while not self.stop_event.is_set():
            if len(self.waveform_queue):
                self.done.clear()
                # If space for adding a waveform
                if (self.pi.wave_get_max_pulses() - self.pi.wave_get_pulses()) > MAX_PULSE_PER_WAVE:
                    logger.debug("Sending New Waveform")
                    wf = self.waveform_queue.popleft()
                    self.pi.wave_add_generic(wf)
                    logger.debug("Loaded Pulses: {}".format(self.pi.wave_get_pulses()))

                    self.current_wid = self.pi.wave_create()
                    # Send the wave
                    self.pi.wave_send_using_mode(self.current_wid,
                        pigpio.WAVE_MODE_ONE_SHOT_SYNC)
                    # Add it to the list of waveforms
                    running_wids.append(self.current_wid)

                msg = "Status: {}, {}".format( self.current_wid, len(self.waveform_queue))
                logger.debug(msg)
            else:
                at = self.pi.wave_tx_at()
                # If not busy
                if at == 9999:
                    self.done.set()
            if len(running_wids):
                at = self.pi.wave_tx_at()
                if at != running_wids[0]:
                    to_delete = running_wids.popleft()
                    self.pi.wave_delete(to_delete)
                    logger.debug("Deleted Wave {}, {} left".format(to_delete, len(running_wids)))


    def cancel(self):
        self.stop_event.set()

