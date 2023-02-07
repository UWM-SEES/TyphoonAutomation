import logging

from typing import Any
from pathlib import Path
from datetime import datetime

from .simulation import Simulation


# TODO: Class diagram documentation for this is incomplete
class Orchestrator(object):
    """ Simulation orchestrator
    
    Organizes and runs simulation scenarios
    """

    def __init__(
            self,
            automator,
            simulation: Simulation):
        from .automator import TyphoonAutomator

        if automator is None:
            raise ValueError("Automator cannot be None")

        if simulation is None:
            raise ValueError("Simulation cannot be None")
            
        self._automator: TyphoonAutomator = automator
        self._simulation = simulation

        self._scenarios = {}
        
        self._data_logging_path: str = None
        self._capture_path: str = None

        self._scenario_exceptions: list = []

    def add_scenario(
            self,
            name: str,
            scenario: Any):
        if not name:
            raise ValueError("Name cannot be empty")

        if scenario is None:
            raise ValueError("Scenario cannot be None")
        
        if name in self._scenarios:
            raise ValueError(f"Scenario name {name} already exists")

        if not hasattr(scenario, "set_up_scenario"):
            raise ValueError("Scenario does not have a set_up_scenario method")
        if not callable(scenario.set_up_scenario):
            raise ValueError("Scenario set_up_scenario attribute is not callable")

        if not hasattr(scenario, "tear_down_scenario"):
            raise ValueError("Scenario does not have a tear_down_scenario method")
        if not callable(scenario.tear_down_scenario):
            raise ValueError("Scenario tear_down_scenario attribute is not callable")

        self._scenarios[name] = scenario

    def run_scenario(
            self,
            name: str):
        if not name:
            raise ValueError("Scenario name cannot be empty")

        if not (name in self._scenarios):
            raise KeyError(f"Scenario {name} does not exist")

        data_log_filename = f"Data_{name}.csv"
        data_log_filename = str(Path(self._data_logging_path) / data_log_filename)

        capture_filename = f"Capture_{name}.csv"
        capture_filename = str(Path(self._capture_path) / capture_filename)

        try:
            self._automator.log(f"*** Running scenario: {name} ***")

            scenario = self._scenarios[name]

            self._simulation.set_data_logging_filename(data_log_filename)
            self._simulation.set_capture_filename(capture_filename)

            self._simulation.initialize(scenario)
            self._simulation.run()

        except BaseException as ex:
            self._automator.log(f"Failed to run scenario {name}", level = logging.ERROR)
            self._scenario_exceptions.append((name, ex))

            self._simulation.stop_simulation()
            self._simulation.stop_data_logger()
            self._simulation.stop_capture()

        finally:
            self._simulation.finalize(scenario)

    def run_all(self):
        self.clear_scenario_exceptions()
        for name in self._scenarios.keys():
            self.run_scenario(name)

    def set_data_logging_path(
            self,
            output_path: str):
        if not output_path:
            raise ValueError("Logging output path cannot be empty")

        try:
            # Create output path if it doesn't exist
            path = Path(output_path)
            if not path.exists():
                path.mkdir(parents = True, exist_ok = True)
        except:
            self._automator.log("Failed to create data logging path", level = logging.ERROR)
            raise
        
        self._data_logging_path = output_path

    def set_capture_path(
            self,
            output_path: str):
        if not output_path:
            raise ValueError("Logging output path cannot be empty")

        try:
            # Create output path if it doesn't exist
            path = Path(output_path)
            if not path.exists():
                path.mkdir(parents = True, exist_ok = True)
        except:
            self._automator.log("Failed to create data logging path", level = logging.ERROR)
            raise

        self._capture_path = output_path

    def get_scenario_exceptions(self) -> list:
        return self._scenario_exceptions

    def clear_scenario_exceptions(self):
        self._scenario_exceptions = []