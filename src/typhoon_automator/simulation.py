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

        self.stop_signal = False
        self.start_time: datetime = None
        self.stop_time: datetime = None

    def initialize(
            self,
            scenario: Any):
        if scenario is None:
            raise ValueError("Scenario cannot be None")

        self.scenario = scenario

    def schedule_event(
            self,
            sim_time: float,
            event: Any):
        raise NotImplementedError()

    def invoke_event(
            self,
            event: Any):
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
        # Start data logger
        self.start_data_logger()
    
        # Start simulation
        self._automator.log("Starting simulation")
        if self.is_simulation_running():
          raise RuntimeError("Simulation is already running")
    
        self.start_time = datetime.now()
        hil.start_simulation()        

    def stop_simulation(self):
        # Stop data logger
        self.stop_data_logger()
                  
        # Stop simulation
        if self.is_simulation_running():
          self._automator.log("Stopping simulation")
          hil.stop_simulation()
        else:
          self_automator.log("Stop simulation called but simulation was not running", level = logger.WARNING)
        
        self.stop_time = datetime.now()

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
        raise NotImplementedError()

    def stop_capture(self):
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
        self.stop_signal = True

    def clear_stop_signal(self):
    """ Clear the simulation stop signal
    """
        self.stop_signal = False

    def get_stop_signal(self) -> bool:
    """ Get the state of the simulation stop signal

    :return State of the stop signal (True for stop, False otherwise)
    """
        return self.stop_signal
