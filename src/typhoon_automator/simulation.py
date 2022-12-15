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

        self._data_log_signals: list[str] = []
        self._data_log_filename: str = None
        self._data_logger_name: str = None


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
            self._automator.log_exception(ex)
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
            self._automator.log_exception(ex)
            raise

    def run(self):
        """ Run the simulation until the stop signal is set
        """
        self.clear_stop_signal()
        self.start_simulation()
        self.start_data_logger()
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
          self._automator.log_exception(ex)
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

    def start_capture(self):
        """ Start the data capture

        :raises ValueError: A configuration value is invalid
        """
        # Ensure configured values are acceptable
        
        # model_timestep
        if self._model._model_timestep <= 0.0:
            raise ValueError(f"Invalid timestep ({self._model._model_timestep})")
        # sample_frequency-- not in model.py?
        # capture_start_time
        # capture duration
        if not self._automator._capture_filename:
            raise ValueError(f"Invalid capture filename ({self._automator.capture_filename})")


        # Initialize capture values
        
        num_analog_channels = len(self._automator._analog_capture_signals)
        # num_samples = int(sample_frequency * capture_duration)
        # decimation = int(1.0 / (self._model._model_timestep * sample_frequency))

        capture_digital = len(self._automator._digital_capture_signals) > 0
        capture_buffer = []
        
        # Start capture
        # self._automator.log(f"Capturing {num_samples} samples starting at sim time {self.config.capture_start_time} to {self.config.capture_filename}")


        # TODO: Clean up capture parameters, e.g. trigger and execute-at time
##        if not hil.start_capture(
##            cpSettings = [
##              decimation,
##              num_analog_channels,
##              num_samples,
##              capture_digital],
##            trSettings = ["Forced"],
##            chSettings = [
##              self._automator._analog_capture_signals,
##              self._automator._digital_capture_signals],
##            dataBuffer = capture_buffer,
##            fileName = self.config.capture_filename,
##            executeAt = self.config.capture_start_time):  # TODO: executeAt doesn't work as expected (perhaps this isn't its correct use)
##            raise RuntimeError("Failed to start capture")

        raise NotImplementedError() # NOT DONE

    def stop_capture(self):
        """ Stop the data capture
    
        :param float timeout: Time to wait for data capture in progress to stop
        """
        # are we using schedule?
        raise NotImplementedError()

    def is_capture_in_progress(self) -> bool:
        """ Check if capture is in progress

        :return True if capture is in progress, false otherwise
        :rtype bool
        """
        return hil.capture_in_progress()

    def start_data_logger(self):
        """ Start the data logger
        """
        if not self._data_logger_name:
            self._automator.log("Data logging not configured, not starting", level = logging.WARNING)
            return

        self._automator.log(f"Starting data logger, file {self._data_log_filename}")
    
        if not hil.add_data_logger(
                name = self._data_logger_name,
                data_file = self._data_log_filename,
                signals = self._data_log_signals,
                use_suffix = False):
            raise RuntimeError("Failed to add data logger")
        
        if not hil.start_data_logger(name = self._data_logger_name):
            raise RuntimeError("Failed to start data logger")

    def stop_data_logger(self):
        """ Stop the data logger
        """
        if not self._data_logger_name:
            self._automator.log("Data logging not configured, not stopping", level = logging.WARNING)
            return

        self._automator.log("Stopping data logger")

        if not hil.stop_data_logger(name = self._data_logger_name):
            self._automator.log("Failed to stop data logger", level = logging.ERROR)
        
        if not hil.remove_data_logger(name = self._data_logger_name):
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
            self._automator.log_exception(ex)
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
            self._automator.log_exception(ex)
            raise

        if sim_running:
            self.start_simulation()

    def configure_data_logging(
            self,
            signals: list[str],
            filename: str):
        if not filename:
            raise ValueError("Filename cannot be empty")

        if (not signals) or (len(signals) < 1):
            raise ValueError("Signal list cannot be empty")

        self._data_log_signals = signals.copy()
        self._data_log_filename = filename

        self._data_logger_name = "SimulationDataLogger"
