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
        raise NotImplementedError()

    def start_simulation(self):
        raise NotImplementedError()

    def stop_simulation(self):
        raise NotImplementedError()

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
