import typhoon.api.hil as hil
import time
import logging

from datetime import datetime
from datetime import timedelta

from typing import Any

from .model import ModelManager
from .schedule import EventSchedule


class Simulation(object):
    """ Simulation interface
    
    Interface for interacting with a simulation
    """

    DATA_LOGGER_NAME: str = "TyphoonAutomator"

    def __init__(
            self,
            automator,
            model: ModelManager):
        from .automator import TyphoonAutomator
        from .automator import Utility

        if automator is None:
            raise ValueError("Automator cannot be None")

        if model is None:
            raise ValueError("Model cannot be None")
            
        self._automator: TyphoonAutomator = automator
        self._utility = Utility
        self._model = model
        
        self._schedule = EventSchedule()

        self._stop_signal = False
        self._start_time: datetime = None
        self._stop_time: datetime = None

        self._scenario_duration: float = 0.0

        self._update_interval = 30.0

        self._data_logging_signals: list[str] = []
        self._data_logging_filename: str = None

        self._analog_capture_signals: list[str] = []
        self._digital_capture_signals: list[str] = []
        self._capture_filename: str = None

    def initialize(
            self,
            scenario: Any):
        if scenario is None:
            raise ValueError("Scenario cannot be None")

        try:
            # Reset scenario duration
            self._scenario_duration = 0.0

            # Set up scenario
            self._automator.log("Initializing scenario")
            scenario.set_up_scenario(self)

            # Ensure valid scenario duration has been set
            if self._scenario_duration <= 0.0:
                raise ValueError(f"Invalid scenario duration ({self._scenario_duration})")

            # Schedule stop event
            stop_event = self._utility.create_callback_event(
                message = "Setting stop signal", 
                callback = Simulation.set_stop_signal)

            self.schedule_event(
                sim_time = self._scenario_duration,
                event = stop_event)
            self.clear_stop_signal()

        except AttributeError:
            if not hasattr(scenario, "set_up_scenario"):
                self._automator.log("Scenario object does not have a set_up_scenario method", level = logging.CRITICAL)
            raise

        except BaseException as ex:
            self._automator.log("Failed to initialize scenario", level = logging.CRITICAL)
            raise

    def finalize(
            self,
            scenario: Any):
        if scenario is None:
            raise ValueError("Scenario cannot be None")

        try:
            self._automator.log("Finalizing scenario")
            scenario.tear_down_scenario(self)

        except AttributeError:
            if not hasattr(scenario, "tear_down_scenario"):
                self._automator.log("Scenario object does not have a tear_down_scenario method", level = logging.CRITICAL)
            raise

        except BaseException as ex:
            self._automator.log("Failed to finalize scenario", level = logging.CRITICAL)
            raise

    def run(self):
        """ Run the simulation until the stop signal is set
        """
        self.clear_stop_signal()
        self.start_data_logger()
        self.start_simulation()
        self._automator.log(f"Scenario started at {self._start_time.strftime('%H:%M:%S, %m/%d/%Y')}")

        last_update_time = datetime.now()

        # Main simulation loop
        while not self.get_stop_signal():
            # TODO: Check simulation health, etc.
            # See utils.py in the Typhoon examples (probably {Typhoon install dir}/examples/tests/utilities_lib)
            if not self.is_simulation_running():
                raise RuntimeError("Simulation stopped running without stop signal")

            # Stop simulation if schedule is empty
            event_count = self._schedule.get_event_count()
            if event_count <= 0:
                self._automator.log("No more events, stopping simulation", level = logging.WARNING)
                self.set_stop_signal()
                break
            
            # Get current simulation time
            simulation_time = self.get_simulation_time()

            # Output simulation time at requested intervals
            if (datetime.now() - last_update_time) >= timedelta(seconds = self._update_interval):
                last_update_time = datetime.now()
                self._automator.log(f"Sim time {simulation_time}, {event_count} events in schedule")
                    
            # Invoke all events scheduled up to and including the current simulation time
            while (self._schedule.has_next_event()):
                if self._schedule.get_next_event_time() > simulation_time:
                    # Next event is scheduled for the future, no more events to invoke right now
                    break

                # Pop next event from schedule and invoke the event
                event = self._schedule.pop_next_event()
                self.invoke_event(event)

        # TODO: This is sloppy fix to allow the data logger to finish logging
        # TODO: See the stop_data_logger function for info on the bug which prompts this
        logger_delay = 3
        self._automator.log(f"Delaying {logger_delay} seconds for data logging flush", level = logging.WARNING)
        time.sleep(logger_delay)

        # Simulation loop is finished, stop simulation
        self.stop_simulation()
        self.stop_data_logger()
        self._automator.log(f"Scenario stopped at {self._stop_time.strftime('%H:%M:%S, %m/%d/%Y')}")

        elapsed_time = self._stop_time - self._start_time
        self._automator.log(f"Elapsed wall time: {elapsed_time.total_seconds()} seconds")

    def schedule_event(
            self,
            sim_time: float,
            event: Any):
        """ Schedule an event to be invoked at a given simulation time

        :param float simulation_time: Simulation time at which to schedule the event
        :param SimulationEvent event: Simulation event to be invoked at the given time
        """
        return self._schedule.add_event(sim_time, event)

    def invoke_event(
            self,
            event: Any):
        """ Invoke an event

        :param SimulationEvent event: Event to be invoked
        """
        try:
            event_time = round(self.get_simulation_time(), 6)
            self._automator.log(f"Event at {event_time}: {event.message}")
            event.invoke(self)
      
        except AttributeError:
          if event is None:
            self._automator.log("Event object cannot be None")
          if not hasattr(event, "invoke"):
            self._automator.log("Event object does not have an invoke method", level = logging.ERROR)
          elif not hasattr(event, "message"):
            self._automator.log("Event object does not have a message", level = logging.ERROR)

        except TypeError:
            if not callable(event.invoke):
                self._automator.log("Event invoke attribute is not callable", level = logging.ERROR)
        
        except BaseException as ex:
          self._automator.log("Event invocation failed", level = logging.CRITICAL)
          raise

    def start_simulation(self):
        """ Start the simulation
        """
        # Start simulation
        self._automator.log("Starting simulation")
        if self.is_simulation_running():
          raise RuntimeError("Simulation is already running")
    
        hil.start_simulation()

        self._start_time = datetime.now()

    def stop_simulation(self):
        """ Stop the simulation
        """
        # Stop simulation
        if self.is_simulation_running():
            self._automator.log("Stopping simulation")
            hil.stop_simulation()

            # Log message if schedule is not empty when stopping
            event_count = self._schedule.get_event_count()
            if event_count > 0:
                self._automator.log(f"Stopped simulation with {event_count} events in schedule")

        else:
            self._automator.log("Stop simulation called but simulation was not running", level = logging.WARNING)
        
        self._stop_time = datetime.now()

    def is_simulation_running(self) -> bool:
        """ Check if the simulation is running

        :return True if simulation is running, false otherwise
        :rtype bool
        """
        return hil.is_simulation_running()

    def get_simulation_time(self) -> float:
        """ Get the current simulation time

        :return Simulation time
        :rtype float
        """
        return hil.get_sim_time()

    def get_simulation_step(self) -> int:
        """ Get the current simulation step
        
        :return Simulation step
        :rtype int
        """
        return hil.get_sim_step()

    def schedule_capture(
            self,
            start_time: float,
            duration: float,
            decimation: int = 1):
        """ Schedule the signal capture

        :param float start_time: Simulation time (in seconds) to start capture
        :param float duration: Simulation time duration (in seconds) of the capture
        :param int decimation: Capture downsampling value
        :raises ValueError: A configuration value is invalid
        """
        if start_time <= 0.0:
            raise ValueError(f"Invalid capture start time ({start_time})")
        
        if duration <= 0.0:
            raise ValueError(f"Invalid capture duration ({duration})")

        if decimation < 1:
            raise ValueError(f"Invalid decimation value ({decimation})")

        if not self._capture_filename:
            raise ValueError(f"Invalid capture filename ({self._capture_filename})")

        MAX_DIGITAL_CAPTURE_SIGNALS = 32
        if len(self._digital_capture_signals) > MAX_DIGITAL_CAPTURE_SIGNALS:
            raise ValueError(f"Invalid number of digital capture signals ({len(self._digital_capture_signals)})")

        timestep = self._model.get_model_timestep()
        if timestep <= 0.0:
            raise ValueError(f"Invalid model timestep ({timestep})")

        # Get start and stop steps
        start_step = self._model.simtime_to_simstep(start_time)
        stop_step = self._model.simtime_to_simstep(start_time + duration)

        # Adjust duration to minimum if needed
        MIN_SAMPLES = 256                       # Per Typhoon's documentation
        if (stop_step - start_step) < MIN_SAMPLES:
            self._automator.log("Capture duration too small, increasing to minimum duration", level = logging.WARNING)
            duration = self._model.simstep_to_simtime(MIN_SAMPLES)
            stop_step = start_step + MIN_SAMPLES

        # Initialize capture info
        num_analog_channels = len(self._analog_capture_signals)
        capture_digital = len(self._digital_capture_signals) > 0
        capture_buffer = []

        num_samples = stop_step - start_step
        if (num_samples & 1) != 0:              # Per Typhoon's documentation, number of samples must be even
            num_samples = num_samples + 1

        capture_settings = [
            decimation,             # Decimation
            num_analog_channels,    # Number of analog channels to capture
            num_samples,            # Number of samples to capture
            capture_digital]        # True to capture digital signals

        # TODO: Consider allowing the user to define a trigger, possibly use a trigger factory to build the settings
        trigger_settings = [
            "Forced"]
        
        channel_settings = [
            self._analog_capture_signals,
            self._digital_capture_signals]  # TODO: Check number of digital channels

        # Schedule capture
        self._automator.log(f"Scheduling capture from {round(start_time, 6)} to {round(start_time + duration, 6)}, file {self._capture_filename}")
        if not hil.start_capture(
                cpSettings = capture_settings,
                trSettings = trigger_settings,
                chSettings = channel_settings,
                dataBuffer = capture_buffer,
                fileName = self._capture_filename,
                executeAt = start_time,
                timeout = None):
            raise RuntimeError("Failed to schedule capture")

    def stop_capture(
            self,
            timeout: float = 0.0):
        """ Stop the data capture
    
        :param float timeout: Time to wait for data capture in progress to stop
        """
        if timeout > 0.0:
            start_time = datetime.now()
            elapsed_time = timedelta(seconds = 0.0)
            self._automator.log(f"Waiting for capture to stop, timeout {timeout}")

            # Wait for capture to stop, timing out if necessary
            while elapsed_time.total_seconds() < timeout:
                if not self.is_capture_in_progress():
                    self._automator.log("Capture stopped")
                    return

                time.sleep(0)   # TODO: Is there a better way to yield without using the threading library?
                elapsed_time = datetime.now() - start_time

        # Stop capture
        if self.is_capture_in_progress():
            self._automator.log("Stopping capture")
            if not hil.stop_capture():
                self._automator.log("Failed to stop capture", level = logging.ERROR)
        else:
            self._automator.log("Stop capture called but capture was not in progress", level = logging.WARNING)

    def is_capture_in_progress(self) -> bool:
        """ Check if capture is in progress

        :return True if capture is in progress, false otherwise
        :rtype bool
        """
        return hil.capture_in_progress()

    def start_data_logger(self):
        """ Start the data logger
        """
        if not self._data_logging_filename:
            self._automator.log("No data logging filename, not starting", level = logging.WARNING)
            return

        if not self._data_logging_signals:
            self._automator.log("No data logging signals, not starting", level = logging.WARNING)
            return

        self._automator.log(f"Starting data logger, file {self._data_logging_filename}")
    
        if not hil.add_data_logger(
                name = Simulation.DATA_LOGGER_NAME,
                data_file = self._data_logging_filename,
                signals = self._data_logging_signals,
                use_suffix = False):
            raise RuntimeError("Failed to add data logger")
        
        if not hil.start_data_logger(name = Simulation.DATA_LOGGER_NAME):
            raise RuntimeError("Failed to start data logger")

    def stop_data_logger(self):
        """ Stop the data logger
        """
        # TODO: Open a Typhoon support ticket for this
        # Error message is always "get_data_logger_status() missing 1 required positional argument: 'name'"
        #status = hil.get_data_logger_status(name = Simulation.DATA_LOGGER_NAME)

        # TODO: Instead of this, use the data logger status to determine if logging needs to be stopped
        if not self._data_logging_filename:
            self._automator.log("No data logging filename, not stopping", level = logging.WARNING)
            return

        self._automator.log("Stopping data logger")

        if not hil.stop_data_logger(name = Simulation.DATA_LOGGER_NAME):
            self._automator.log("Failed to stop data logger", level = logging.ERROR)
        
        if not hil.remove_data_logger(name = Simulation.DATA_LOGGER_NAME):
            self._automator.log("Failed to remove data logger", level = logging.ERROR)

    def set_stop_signal(self):
        """ Set the simulation stop signal
        """
        self._automator.log("Setting stop signal")
        self._stop_signal = True

    def clear_stop_signal(self):
        """ Clear the simulation stop signal
        """
        self._stop_signal = False

    def get_stop_signal(self) -> bool:
        """ Get the state of the simulation stop signal

        :return State of the stop signal (True for stop, False otherwise)
        """
        return self._stop_signal

    def set_scenario_duration(
            self,
            duration: float):
        if duration <= 0.0:
            raise ValueError(f"Invalid scenario duration ({duration})")
        
        self._scenario_duration = duration

    def save_model_state(
            self,
            filename: str):
        if not filename:
            raise ValueError("Filename cannot be empty")

        sim_running = self.is_simulation_running()
        self._automator.log(f"Saving model to {filename}, simulation running: {sim_running}")

        if sim_running:
            self.stop_simulation()

        try:
            self._model.save_model_state(filename)
        except BaseException as ex:
            self._automator.log("Failed to save model state", level = logging.CRITICAL)
            raise

        if sim_running:
            self.start_simulation()

    def load_model_state(
            self,
            filename: str):
        if not filename:
            raise ValueError("Filename cannot be empty")

        sim_running = self.is_simulation_running()
        self._automator.log(f"Loading model from {filename}, simulation running: {sim_running}")

        if sim_running:
            self.stop_simulation()

        try:
            self._model.load_model_state(filename)
        except BaseException as ex:
            self._automator.log("Failed to load model state", level = logging.CRITICAL)
            raise

        if sim_running:
            self.start_simulation()

    def set_data_logging_signals(
            self,
            signals: list[str]):
        if signals is None:
            raise ValueError("Data logging signal list cannot be None")

        self._data_logging_signals = signals.copy()

    def set_data_logging_filename(
            self,
            filename: str):
        if not filename:
            raise ValueError("Filename cannot be empty")

        self._data_logging_filename = filename

    def set_capture_signals(
            self,
            analog_signals: list[str],
            digital_signals: list[str]):
        if analog_signals is None:
            raise ValueError("Analog signal list cannot be None")

        if digital_signals is None:
            raise ValueError("Digital signal list cannot be None")

        self._analog_capture_signals = analog_signals.copy()
        self._digital_capture_signals = digital_signals.copy()

    def set_capture_filename(
            self,
            filename: str):
        if not filename:
            raise ValueError("Filename cannot be empty")

        self._capture_filename = filename

    def set_scada_value(
            self,
            name: str,
            value: Any):
        self._model.set_scada_value(name = name, value = value)
