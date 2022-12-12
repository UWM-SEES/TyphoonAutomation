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
        self._model = simulation

        self._scenarios: list[Any] = []

    def add_scenario(
            self,
            scenario: Any):
        if scenario is None:
          raise ValueError("Scenario cannot be None")
        self._scenarios.add(scenario)

    def run(self):
        raise NotImplementedError()
