from typing import Any

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

        try:
            self._automator.log(f"*** Running scenario: {name} ***")

            scenario = self._scenarios[name]
            self._simulation.initialize(scenario)
            self._simulation.run()
            self._simulation.finalize(scenario)

        except BaseException as ex:
            self._automator.log(f"Failed to run scenario {name}")
            self._automator.log_exception(ex)
            raise

    def run_all(self):
        for name in self._scenarios.keys():
            self.run_scenario(name)
