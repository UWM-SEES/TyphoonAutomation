import typhoon.api.hil as hil
import time

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
            automator):
        from .automator import TyphoonAutomator

        if automator is None:
            raise ValueError("Automator cannot be none")
            
        self._automator: TyphoonAutomator = automator

        # TODO: Consider creating a factory function to address this ModelManager dependency
        self._model = self._automator._model
        
        self._schedule = EventSchedule()

        self._stop_signal = False
        self._start_time: datetime = None
        self._stop_time: datetime = None

    def initialize(
            self,
            scenario: Any):
        # TODO: Orchestrator owns scenarios, Simulation initializes them-- make changes
        if scenario is None:
            raise ValueError("Scenario cannot be None")

        self._automator._orchestrator.add_scenario(scenario)

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
        if event is None:
            raise ValueError("Event cannot be None")
        try:
            event_time = round(self.get_simulation_time(), 6)
            self._automator.log(f"Event at {event_time}: {event.message}")
            event.invoke(self)
      
        except AttributeError:
          if not hasattr(event, "invoke"):
            self._automator.log("Event object does not have an invoke method", level = logging.ERROR) # is this the right level?
          elif not hasattr(event, "message"):
            self._automator.log("Event object does not have a message", level = logging.ERROR)
        
        except BaseException as ex:
          self._automator.log("Event invocation failed", level = logging.ERROR)
          self._automator.log_exception(ex)
          raise

    def start_simulation(self):
    """ Start the simulation
    """
        # Start data logger
        self.start_data_logger()
    
        # Start simulation
        self._automator.log("Starting simulation")
        if self.is_simulation_running():
          raise RuntimeError("Simulation is already running")
    
        self._start_time = datetime.now()
        hil.start_simulation()        

    def stop_simulation(self):
    """ Stop the simulation
    """
        # Stop data logger
        self.stop_data_logger()
                  
        # Stop simulation
        if self.is_simulation_running():
          self._automator.log("Stopping simulation")
          hil.stop_simulation()
        else:
          self._automator.log("Stop simulation called but simulation was not running", level = logger.WARNING)
        
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
        raise NotImplementedError()

    def stop_data_logger(self):
    """ Stop the data logger
    """
        raise NotImplementedError()

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
