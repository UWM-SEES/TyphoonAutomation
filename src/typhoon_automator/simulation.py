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

        self.start_time: datetime = None
        self.stop_time: datetime = None

    def initialize(
            self,
            scenario: Any):
        raise NotImplementedError()

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
        raise NotImplementedError()

    def get_simulation_time(self) -> float:
        raise NotImplementedError()

    def get_simulation_step(self) -> int:
        raise NotImplementedError()

    def start_capture(self):
        raise NotImplementedError()

    def stop_capture(self):
        raise NotImplementedError()

    def is_capture_in_progress(self) -> bool:
        # TODO: Return type is missing from class diagram
        raise NotImplementedError()

    def start_data_logger(self):
        raise NotImplementedError()

    def stop_data_logger(self):
        raise NotImplementedError()

    def set_stop_signal(self):
        raise NotImplementedError()

    def clear_stop_signal(self):
        raise NotImplementedError()

    def get_stop_signal(self) -> bool:
        raise NotImplementedError()
